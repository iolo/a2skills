-- Private, single-flight file transport. Not a remote service or a Lua sandbox.
local exports = {name='a2_mailbox', version='1.0.0', description='Owned session mailbox'}
function exports.startplugin()
    local directory = assert(os.getenv('A2_MAME_SESSION')) .. '/mailbox'
    local scripts = assert(os.getenv('A2_MAME_SCRIPTS'))
    local json = require('json')
    local state, busy = 'starting', false
    local function write(path, value)
        local encoded = json.stringify(value)
        local f = assert(io.open(path .. '.tmp', 'wb'))
        assert(f:write(encoded, '\n')); assert(f:close())
        assert(os.rename(path .. '.tmp', path))
    end
    local function exists(path)
        local f = io.open(path, 'rb')
        if f then f:close(); return true end
        return false
    end
    local function process()
        if state == 'failed' then return end
        if state == 'starting' then
            local m = manager.machine
            local cpu = m and m.devices[':maincpu']
            if not cpu or not cpu.spaces.program or not m.debugger or not cpu.state.PC then return end
            local ok, err = pcall(function()
                a2 = dofile(scripts .. '/control.lua')
                a2_automation = dofile(scripts .. '/automation.lua')
                local startup = os.getenv('A2_MAME_STARTUP')
                if startup then dofile(startup) end
            end)
            state = ok and 'ready' or 'failed'
            write(directory .. '/ready.json', {ok=ok, error=not ok and tostring(err) or nil,
                driver=m.system.name, version=emu.app_version(), transport='a2-mailbox-v1'})
            if not ok then
                if a2_automation then pcall(a2_automation.stop, 'startup failed') end
                return
            end
        end
        local pending = directory .. '/request.json'
        local f = io.open(pending, 'rb')
        if not f then return end
        local raw = f:read('a'); f:close()
        local parsed, request = pcall(json.parse, raw)
        if not parsed or type(request) ~= 'table' or type(request.id) ~= 'string'
            or not request.id:match('^[a-z0-9-]+$') or #request.id > 64 then
            assert(os.rename(pending, directory .. '/invalid-request.json'))
            write(directory .. '/protocol-error.json', {ok=false, error='invalid request ID/JSON; start a fresh session'})
            state = 'failed'; return
        end
        local prefix = directory .. '/' .. request.id
        assert(not exists(prefix .. '.request.json') and not exists(prefix .. '.response.json'), 'duplicate request ID')
        assert(os.rename(pending, prefix .. '.request.json')) -- evidence before effects
        local ok, result = pcall(function()
            if request.operation then
                assert(request.operation ~= 'call' and type(a2[request.operation]) == 'function', 'unknown operation')
                return a2[request.operation](table.unpack(request.args or {}))
            end
            assert(type(request.code) == 'string' and #request.code <= 65536, 'Lua source required (max 65536 bytes)')
            local fn, err = load(request.code, 'mailbox:' .. request.id, 't', _G)
            assert(fn, err)
            return fn()
        end)
        local response = {id=request.id, ok=ok, result=ok and result or nil, error=not ok and tostring(result) or nil}
        local encoded, err = pcall(write, prefix .. '.response.json', response)
        if not encoded then
            write(prefix .. '.response.json', {id=request.id, ok=false,
                error='operation may have executed; receipt encoding failed: ' .. tostring(err)})
        end
    end
    -- Host periodic callback continues through ordinary pause AND debugger stop.
    emu.register_periodic(function()
        if busy or state == 'failed' then return end
        busy = true
        local ok, err = pcall(process)
        if not ok then
            state = 'failed'
            pcall(write, directory .. '/transport-error.json', {ok=false, error=tostring(err)})
        end
        busy = false
    end)
end
return exports
