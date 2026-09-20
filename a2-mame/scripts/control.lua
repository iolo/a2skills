-- MAME Lua console helpers. Resolve machine/device objects for every operation:
-- resets can invalidate previously retained objects. No background transport.
local a2 = {}
local json = require('json')
local function machine() return manager.machine end
local function integer(value, low, high)
    assert(type(value) == 'number' and value % 1 == 0 and value >= low and value <= high,
           'integer outside allowed range')
    return value
end
local function cpu(tag)
    local d = machine().devices[tag or ':maincpu']
    assert(d and d.spaces and d.spaces.program and d.state, 'CPU/program space unavailable; inspect devices')
    return d
end
local function stable()
    assert(machine().paused or (machine().debugger and machine().debugger.execution_state == 'stop'),
           'pause or stop in debugger first')
end
local function range(address, length)
    integer(address, 0, 65535)
    integer(length, 1, 4096)
    assert(address + length <= 65536, 'range crosses 64K')
    assert(address + length <= 0xC000 or address >= 0xD000,
           'helper refuses mapped I/O/soft-switch range $C000-$CFFF')
end
function a2.status()
    local m = machine()
    return {version=emu.app_version(), driver=m.system.name, paused=m.paused,
            debugger=m.debugger and m.debugger.execution_state or 'disabled', time=m.time:as_double()}
end
function a2.devices()
    local r = {cpus={}, images={}, screens={}}
    for tag, d in pairs(machine().devices) do
        if d.spaces and d.spaces.program and d.state then r.cpus[#r.cpus+1] = tag end
    end
    for tag, d in pairs(machine().images) do
        r.images[#r.images+1] = {tag=tag, instance=d.instance_name, filename=d.filename}
    end
    for tag, _ in pairs(machine().screens) do r.screens[#r.screens+1] = tag end
    return r
end
function a2.pause() emu.pause(); return a2.status() end
function a2.resume()
    assert(not machine().debugger or machine().debugger.execution_state ~= 'stop',
           'debugger is stopped; use go')
    emu.unpause()
    return a2.status()
end
function a2.reset() machine():soft_reset(); return {scheduled='soft_reset'} end
function a2.registers(tag)
    stable()
    local r = {}
    for name, entry in pairs(cpu(tag).state) do r[name] = entry.value end
    return r
end
function a2.set_register(name, value, tag)
    stable()
    local limits = {PC=65535, A=255, X=255, Y=255, SP=511, P=255}
    assert(limits[name], 'use PC/A/X/Y/SP/P; inspect registers for this CPU')
    integer(value, name == 'SP' and 256 or 0, limits[name])
    local entry = assert(cpu(tag).state[name], 'register unavailable')
    entry.value = value
    return a2.registers(tag)
end
function a2.read(address, length, tag)
    stable(); range(address, length)
    local space, r = cpu(tag).spaces.program, {}
    for i=0,length-1 do r[#r+1] = space:read_u8(address+i) end
    return {address=address, bytes=r, mapping='CPU-visible'}
end
function a2.write(address, bytes, tag)
    stable(); range(address, #bytes)
    for _, value in ipairs(bytes) do integer(value, 0, 255) end
    local space = cpu(tag).spaces.program
    for i,value in ipairs(bytes) do space:write_u8(address+i-1, value) end
    local result = a2.read(address, #bytes, tag)
    for i,value in ipairs(bytes) do assert(result.bytes[i] == value, 'write read-back mismatch; partial effects possible') end
    return result
end
function a2.load_binary(path, address, tag)
    stable()
    local f = assert(io.open(path, 'rb'))
    local data = f:read(4097); f:close()
    assert(data and #data > 0 and #data <= 4096, 'raw fixture must contain 1–4096 bytes')
    assert(data:sub(1,4) ~= '\0\5\22\0', 'AppleSingle is not a raw binary')
    local bytes = {data:byte(1,#data)}
    return a2.write(address, bytes, tag)
end
function a2.keys(text)
    assert(not machine().paused and (not machine().debugger or machine().debugger.execution_state == 'run'),
           'resume execution before keyboard input')
    assert(type(text) == 'string' and #text > 0 and #text <= 256, 'send 1–256 bytes')
    machine().natkeyboard:post(text)
    return {queued=true} -- not proof of program consumption
end
local function image(tag) return assert(machine().images[tag], 'unknown image tag; inspect devices') end
function a2.mount(tag, path)
    local err, message = image(tag):load(path)
    assert(not err, message or tostring(err))
    return {filename=image(tag).filename}
end
function a2.eject(tag) image(tag):unload(); return {filename=image(tag).filename} end
function a2.screenshot(path, tag)
    local screen = tag and machine().screens[tag]
    if not tag then
        for _, candidate in pairs(machine().screens) do
            assert(not screen, 'multiple screens: provide a tag'); screen = candidate
        end
    end
    assert(screen, 'no screen found')
    local err = screen:snapshot(path)
    assert(not err, tostring(err))
    return {path=path}
end
function a2.save(path) machine():save(path); return {scheduled='save', path=path} end
function a2.restore(path) machine():load(path); return {scheduled='load', path=path} end
local function debug_cpu(tag)
    assert(machine().debugger, 'launch with --debug')
    return assert(cpu(tag).debug, 'CPU debugger unavailable')
end
function a2.breakpoint(address, tag)
    integer(address, 0, 65535)
    -- 0.285 binds condition/action as C strings; supply both, never nil.
    return {id=debug_cpu(tag):bpset(address, '1', '')}
end
function a2.clear_breakpoint(id, tag)
    integer(id, 1, 0x7FFFFFFF)
    return {cleared=debug_cpu(tag):bpclear(id)}
end
function a2.go(tag)
    local d = debug_cpu(tag)
    emu.unpause(); d:go()
    return {scheduled='go'}
end
function a2.step(tag)
    assert(machine().debugger and machine().debugger.execution_state == 'stop', 'stop in debugger before stepping')
    emu.unpause(); debug_cpu(tag):step(1)
    return {scheduled='step'}
end
function a2.exit() machine():exit(); return {scheduled='exit'} end
function a2.call(id, operation, ...)
    assert(type(id) == 'string' and #id <= 64, 'provide a short command id')
    local fn = a2[operation]
    local ok, result
    if type(fn) == 'function' and operation ~= 'call' then
        ok, result = pcall(fn, ...)
    else ok, result = false, 'unknown operation' end
    print('A2 ' .. json.stringify({id=id, ok=ok, result=ok and result or nil, error=not ok and tostring(result) or nil}))
end
return a2
