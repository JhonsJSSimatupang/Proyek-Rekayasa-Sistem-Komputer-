function n = wire_sihadir_model(modelFile)
%WIRE_SIHADIR_MODEL  Wire the SiHADIR architecture with real connector lines.
%
%   n = wire_sihadir_model(modelFile) opens the model, draws one line per
%   link in SIHADIR_ARCH_SPEC and saves. Returns the number of lines drawn.
%
%   Why this exists: on this MATLAB installation systemcomposer's
%   connect()/Architecture.connect() return a Connector object but never
%   create a line, so the saved model has no connectors at all. The
%   underlying Simulink line API works, and System Composer reads saved
%   lines back as connectors (verified: after save+reload,
%   Architecture.Connectors is populated). This function therefore performs
%   the wiring at the line level while keeping the architecture model
%   exactly as System Composer stores it.
%
%   See also BUILD_SIHADIR_ARCHITECTURE, SIHADIR_ARCH_SPEC.

if nargin < 1 || isempty(modelFile)
    modelFile = fullfile(pwd, 'SiHADIR_Architecture.slx');
end
[~, modelName] = fileparts(modelFile);
assert(isfile(modelFile), 'Model tidak ditemukan: %s', modelFile);

spec = sihadir_arch_spec();
if bdIsLoaded(modelName)
    close_system(modelName, 0);
end
load_system(modelName);
model = systemcomposer.loadModel(modelFile);
arch  = model.Architecture;

subMap  = containers.Map('KeyType', 'char', 'ValueType', 'any');
compMap = containers.Map('KeyType', 'char', 'ValueType', 'any');
subs = arch.Components;
for k = 1:numel(subs)
    sid = extractId(subs(k).Name);
    subMap(sid) = subs(k);
    kids = subs(k).Architecture.Components;
    for j = 1:numel(kids)
        compMap(extractId(kids(j).Name)) = kids(j);
    end
end

n = 0;
skipped = {};
for k = 1:numel(spec.links)
    l = spec.links(k);
    subSrc = componentSubsystem(spec, l.src);
    subDst = componentSubsystem(spec, l.dst);
    cSrc = compMap(l.src);
    cDst = compMap(l.dst);

    hSrc = cSrc.getPort(l.srcPort).SimulinkHandle;
    hDst = cDst.getPort(l.dstPort).SimulinkHandle;

    try
        if strcmp(subSrc, subDst)
            sys = get_param(get_param(hSrc, 'Parent'), 'Parent');
            add_line(sys, hSrc, hDst, 'autorouting', 'on');
            n = n + 1;
            continue
        end

        sSrc = subMap(subSrc);
        sDst = subMap(subDst);
        sysSrc = getfullname(sSrc.SimulinkHandle);   % the subsystem itself
        sysDst = getfullname(sDst.SimulinkHandle);

        % inner: component -> boundary port of its own subsystem
        bpOut = sSrc.getPort(boundaryName(l.src, l.srcPort)).SimulinkHandle;
        hIn   = innerSide(sSrc.SimulinkHandle, bpOut, 'Outport');
        add_line(sysSrc, hSrc, hIn, 'autorouting', 'on');
        n = n + 1;

        % inner: boundary port of the destination subsystem -> component
        bpIn = sDst.getPort(boundaryName(l.dst, l.dstPort)).SimulinkHandle;
        hOut = innerSide(sDst.SimulinkHandle, bpIn, 'Inport');
        add_line(sysDst, hOut, hDst, 'autorouting', 'on');
        n = n + 1;

        % outer: the visible cable between the two subsystems
        rootSys = get_param(sysSrc, 'Parent');
        add_line(rootSys, bpOut, bpIn, 'autorouting', 'on');
        n = n + 1;
    catch err
        where = '';
        if ~isempty(err.stack)
            where = sprintf(' [%s:%d]', err.stack(1).name, err.stack(1).line);
        end
        skipped{end+1} = sprintf('%s.%s -> %s.%s : %s%s', ...
            l.src, l.srcPort, l.dst, l.dstPort, err.message, where); %#ok<AGROW>
    end
end

model.save();
model.close();
close_system(modelName, 0);

fprintf('Garis terpasang: %d\n', n);
for k = 1:numel(skipped)
    fprintf('  GAGAL %s\n', skipped{k});
end
if ~isempty(skipped)
    warning('sihadir:wire', '%d link gagal disambung.', numel(skipped));
end
end

% ======================================================================
function h = innerSide(subBlk, hExternal, blockType)
%INNERSIDE  Port handle of the port block that backs a subsystem boundary
%port, seen from inside the subsystem.
ph = get_param(subBlk, 'PortHandles');
if strcmp(blockType, 'Outport')
    k = find(ph.Outport == hExternal, 1);
else
    k = find(ph.Inport == hExternal, 1);
end
assert(~isempty(k), 'Port boundary tidak ditemukan pada %s', subBlk);

blks = find_system(subBlk, 'SearchDepth', 1, 'BlockType', blockType);
% find_system answers with handles when it is given a handle, and with char
% when there is a single hit; normalise both so callers always see paths.
if isnumeric(blks)
    blks = arrayfun(@(x) getfullname(x), blks, 'UniformOutput', false);
end
if ischar(blks)
    blks = {blks};
end
for b = 1:numel(blks)
    if str2double(get_param(blks{b}, 'Port')) == k
        bh = get_param(blks{b}, 'PortHandles');
        if strcmp(blockType, 'Outport')
            h = bh.Inport;      % inside view of an Outport block
        else
            h = bh.Outport;     % inside view of an Inport block
        end
        return
    end
end
error('Blok %s nomor %d tidak ditemukan di %s', blockType, k, subBlk);
end

% ======================================================================
function id = extractId(name)
%EXTRACTID  "C1.3 Terminal Application" -> "C1.3"; "S1 Edge Terminal" -> "S1".
t = regexp(char(string(name)), '^(S\d+|C\d+\.\d+)', 'tokens', 'once');
if isempty(t)
    error('sihadir:name', 'Nama tanpa ID: %s', string(name));
end
id = t{1};
end

% ======================================================================
function name = boundaryName(compId, portName)
name = sprintf('%s_%s', strrep(compId, '.', '_'), portName);
end

% ======================================================================
function s = componentSubsystem(spec, compId)
idx = find(strcmp({spec.components.id}, compId), 1);
s = spec.components(idx).subsystem;
end
