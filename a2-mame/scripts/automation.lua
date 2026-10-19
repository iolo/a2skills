-- Bounded, single-controller breakpoint dispatch for program-specific adapters.
-- Re-loading this module cannot create a second controller registry.
if a2_automation then return a2_automation end
local api = {current=nil}
local json = require('json')
local function write_result(path, value)
    local encoded = json.stringify(value)
    local f = assert(io.open(path .. '.tmp', 'wb'))
    assert(f:write(encoded, '\n')); assert(f:close())
    assert(os.rename(path .. '.tmp', path))
end
function api.busy() return api.current ~= nil and api.current.active end
function api.stop(reason)
    if api.busy() then return api.current:finish(false, reason or 'stopped by host') end
    return {active=false}
end
function api.new(options)
    assert(not api.busy(), 'one execution controller per session')
    assert(type(options.result_path) == 'string', 'unique result_path required')
    local existing = io.open(options.result_path, 'rb')
    if existing then existing:close(); error('result_path already exists') end
    local timeout = options.progress_timeout or 180
    assert(type(timeout) == 'number' and timeout > 0 and timeout < math.huge, 'finite progress_timeout required')
    local m = manager.machine
    local cpu = assert(m.devices[options.cpu_tag or ':maincpu'])
    assert(m.debugger and m.debugger.execution_state == 'stop', 'create controller at a debugger stop')
    assert(type(emu.add_machine_post_load_notifier) == 'function' and
           type(emu.add_machine_stop_notifier) == 'function', 'MAME lifecycle notifier API required')
    local r = {active=true, started=os.time(), progress=os.time(), steps=0,
               ids={}, handlers={}, subscriptions={}, phase_name='unconfigured'}
    local space = cpu.spaces.program
    local pending, tap, allowed
    api.current = r
    function r:finish(ok, reason, detail)
        if not self.active then return self.result end
        self.active = false
        pending = nil
        local errors = {}
        local function cleanup(fn)
            local success, err = pcall(fn)
            if not success then errors[#errors+1] = tostring(err) end
        end
        if tap then cleanup(function() tap:remove() end); tap = nil end
        for _, id in ipairs(self.ids) do cleanup(function() cpu.debug:bpclear(id) end) end
        self.ids = {}
        for _, sub in ipairs(self.subscriptions) do cleanup(function() sub:unsubscribe() end) end
        self.subscriptions = {}
        emu.pause() -- never automatically run past completion or an unexpected stop
        self.result = {ok=ok and #errors == 0, reason=reason, detail=detail, phase=self.phase_name,
                       pc=cpu.state.PC.value, steps=self.steps, host_seconds=os.time()-self.started,
                       emulated_seconds=m.time:as_double(), cleanup_errors=errors}
        local saved, err = pcall(write_result, options.result_path, self.result)
        if not saved then
            -- Bad adapter detail must not conceal failure behind a clean exit.
            self.result.ok, self.result.detail = false, nil
            self.result.receipt_error = tostring(err)
            local recovered, failure = pcall(write_result, options.result_path, self.result)
            if not recovered then emu.print_error('automation receipt failed: ' .. tostring(failure)) end
        end
        return self.result
    end
    function r:phase(name, handlers, guard)
        assert(self.active and m.debugger.execution_state == 'stop', 'phase change requires active debugger stop')
        assert(pending == nil, 'pending key must be consumed before changing modules')
        assert(type(name) == 'string' and type(guard) == 'function', 'phase identity and bank/module guard required')
        assert(guard(), 'module/bank identity rejected')
        for _, id in ipairs(self.ids) do cpu.debug:bpclear(id) end
        self.ids, self.handlers, self.guard, self.phase_name = {}, {}, guard, name
        allowed = nil -- new overlay must explicitly declare its keyboard polling sites
        for address, handler in pairs(handlers) do
            assert(type(address) == 'number' and address % 1 == 0 and address >= 0 and address <= 65535)
            assert(type(handler) == 'function', 'handler must be a function')
            self.ids[#self.ids+1] = cpu.debug:bpset(address, '1', '')
            self.handlers[address] = handler
        end
    end
    function r:keyboard(polling_addresses)
        assert(self.active and m.debugger.execution_state == 'stop', 'configure keyboard while stopped')
        assert(pending == nil, 'pending key not consumed')
        allowed = {}
        for _, address in ipairs(polling_addresses) do
            assert(self.handlers[address], 'poll site must have an owned handler in current phase')
            allowed[address] = true
        end
        if not tap then
            tap = space:install_read_tap(0xC000, 0xC000, 'a2-one-shot-key', function(_, data)
                if pending ~= nil and not m:side_effects_disabled() then
                    local value = pending; pending = nil
                    return value | 0x80
                end
                return data
            end)
        end
    end
    function r:pending_key() return pending end
    function r:key(value)
        assert(self.active and m.debugger.execution_state == 'stop', 'arm only at debugger stop')
        local pc = cpu.state.PC.value
        assert(allowed and allowed[pc], 'PC is not an adapter-approved polling instruction')
        assert(self.guard(), 'module/bank identity changed')
        assert(space:read_u8(pc) == 0xAD and space:read_u8(pc+1) == 0 and space:read_u8(pc+2) == 0xC0,
               'poll opcode must be LDA $C000 (AD 00 C0)')
        assert(pending == nil, 'previous key has not been consumed')
        assert(type(value) == 'number' and value % 1 == 0 and value >= 0 and value <= 127, '7-bit key required')
        pending = value
    end
    local function invalidate(reason)
        if r.active then r:finish(false, reason .. '; create a new controller and reacquire mapping/symbols') end
    end
    -- Reset/load invalidates the controller; no automatic recovery with stale handles.
    emu.register_prestart(function() invalidate('reset') end)
    r.subscriptions[#r.subscriptions+1] = emu.add_machine_post_load_notifier(function() invalidate('state loaded') end)
    r.subscriptions[#r.subscriptions+1] = emu.add_machine_stop_notifier(function() invalidate('machine stopped') end)
    emu.register_periodic(function()
        if not r.active then return end
        local ok, err = pcall(function()
            assert(os.time() - r.progress < timeout, 'host progress watchdog expired')
            if m.debugger.execution_state ~= 'stop' then return end
            local pc = cpu.state.PC.value
            local handler = assert(r.handlers[pc], string.format('unexpected debugger stop at $%04X', pc))
            assert(r.guard(), 'module/bank identity changed')
            assert(pending == nil, 'previous key was not consumed at next stop')
            r.steps = r.steps + 1
            handler(r)
            r.progress = os.time()
            if r.active then emu.unpause(); cpu.debug:go() end
        end)
        if not ok then
            local saved, save_error = pcall(function() r:finish(false, tostring(err)) end)
            if not saved then emu.print_error('automation receipt failed: ' .. tostring(save_error)) end
        end
    end)
    return r
end
return api
