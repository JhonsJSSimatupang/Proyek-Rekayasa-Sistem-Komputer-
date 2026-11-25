function build_sihadir_architecture(outFile)
%BUILD_SIHADIR_ARCHITECTURE  Build the SiHADIR physical architecture model.
%
%   Materialises SIHADIR_ARCH_SPEC into a System Composer model:
%     model -> interface dictionary -> 6 composite subsystems ->
%     33 components -> 64 ports -> 16 interfaces -> 22 links -> save
%
%   A link whose endpoints live in different subsystems is routed through a
%   boundary port on the source and on the destination subsystem. That is how
%   System Composer represents a connection leaving a composite, and it keeps
%   the top-level diagram readable while the detailed wiring stays inside.
%
%   build_sihadir_architecture()      writes SiHADIR_Architecture.slx in pwd.
%   build_sihadir_architecture(file)  writes to the given .slx path.
%
%   API notes for this release (verified by probe_api3):
%     addPort(architecture, name, dir)   dir is 'in' or 'out'
%     comp.getPort(name)                 external view used for connect
%     connect(architecture, src, dst)    both ends in the same architecture
%     addElement(iface, name, Type=...)  Type must be a built-in MATLAB type
%     interface names must be valid MATLAB identifiers -> SIHADIR_IFACE_NAME
%
%   See also SIHADIR_ARCH_SPEC, SIHADIR_IFACE_NAME, VERIFY_BUILT_MODEL.

if nargin < 1 || isempty(outFile)
    outFile = fullfile(pwd, 'SiHADIR_Architecture.slx');
end
[outDir, modelName] = fileparts(outFile);
if isempty(outDir)
    outDir = pwd;
end
modelName = char(modelName);

spec = sihadir_arch_spec();

% ------------------------------------------------------------------ 0. reset
if bdIsLoaded(modelName)
    close_system(modelName, 0);
end
if isfile(outFile)
    delete(outFile);
end
Simulink.data.dictionary.closeAll('-discard');
dictPath = fullfile(outDir, [modelName '_Interfaces.sldd']);
if isfile(dictPath)
    delete(dictPath);
end

log('Membangun model %s', modelName);

% ------------------------------------------------------------------ 1. model
model = systemcomposer.createModel(modelName);
arch  = model.Architecture;
log('model dibuat: %s', modelName);

% ------------------------------------------------------------- 2. dictionary
dict = systemcomposer.createDictionary(dictPath);
for k = 1:numel(spec.interfaces)
    iface = addInterface(dict, sihadir_iface_name(spec.interfaces(k).id));
    els = spec.interfaces(k).elements;
    for e = 1:numel(els)
        parts = split(string(els{e}), ':');
        addElement(iface, char(parts(1)), Type=matlabType(parts(2)));
    end
end
dict.save();
model.linkDictionary(dictPath);
log('dictionary: %d interface', numel(spec.interfaces));

% ------------------------------------------------------------ 3. subsystems
subMap = containers.Map('KeyType', 'char', 'ValueType', 'any');
for k = 1:numel(spec.subsystems)
    s = spec.subsystems(k);
    subMap(s.id) = addComponent(arch, sprintf('%s %s', s.id, s.name));
end
log('subsistem: %d', numel(spec.subsystems));

% ------------------------------------------------------------ 4. components
compMap = containers.Map('KeyType', 'char', 'ValueType', 'any');
for k = 1:numel(spec.components)
    c = spec.components(k);
    compMap(c.id) = addComponent(subMap(c.subsystem).Architecture, ...
        sprintf('%s %s', c.id, c.name));
end
log('komponen: %d', numel(spec.components));

% ----------------------------------------------------------------- 5. ports
% portMap keeps the architecture-side handle, which is the one that carries
% the interface. Connections use comp.getPort(), the component-side handle.
portMap = containers.Map('KeyType', 'char', 'ValueType', 'any');
for k = 1:numel(spec.ports)
    p = spec.ports(k);
    portMap(portKey(p.comp, p.name)) = ...
        addPort(compMap(p.comp).Architecture, p.name, portDir(p.dir));
end
log('port: %d', numel(spec.ports));

% ------------------------------------------------------- 6. port interfaces
nIf = 0;
for k = 1:numel(spec.ports)
    p = spec.ports(k);
    if strcmp(p.interface, 'internal')
        continue
    end
    iface = dict.getInterface(sihadir_iface_name(p.interface));
    hPort = portMap(portKey(p.comp, p.name));   % method needs a real lvalue
    hPort.setInterface(iface);
    nIf = nIf + 1;
end
log('interface terpasang: %d port', nIf);

% ------------------------------------------------------- 7. boundary ports
% Cross-subsystem links need a port on each composite so the connection can
% leave and re-enter a subsystem. Creating the ports here keeps the model
% structure complete even if the wiring step below has to be re-run.
nBoundary = 0;
for k = 1:numel(spec.links)
    l = spec.links(k);
    subSrc = componentSubsystem(spec, l.src);
    subDst = componentSubsystem(spec, l.dst);
    if strcmp(subSrc, subDst)
        continue
    end
    hSrcSub = subMap(subSrc);
    hDstSub = subMap(subDst);
    bpOut = addPort(hSrcSub.Architecture, boundaryName(l.src, l.srcPort), 'out');
    attachIf(bpOut, l.interface, dict);
    bpIn = addPort(hDstSub.Architecture, boundaryName(l.dst, l.dstPort), 'in');
    attachIf(bpIn, l.interface, dict);
    nBoundary = nBoundary + 2;
end
log('boundary port: %d', nBoundary);

% ------------------------------------------------------------------ 8. save
model.save();
model.close();

% ----------------------------------------------------------------- 9. wire
% connect() on this installation returns a Connector but writes no line, so
% the wiring is done at the line level (see WIRE_SIHADIR_MODEL for the why).
wire_sihadir_model(outFile);

log('tersimpan: %s', outFile);
fprintf('Selesai. Jalankan verify_built_model untuk memeriksa artefaknya.\n');
end

% ======================================================================
function attachIf(port, ifaceId, dict)
if strcmp(ifaceId, 'internal')
    return
end
port.setInterface(dict.getInterface(sihadir_iface_name(ifaceId)));
end

% ======================================================================
function d = portDir(specDir)
%PORTDIR  The spec already uses the values addPort expects.
if startsWith(lower(string(specDir)), "o")
    d = 'out';
else
    d = 'in';
end
end

% ======================================================================
function t = matlabType(logicalType)
%MATLABTYPE  Map spec logical types to types the bus compiler can resolve.
switch lower(string(logicalType))
    case {"double", "score", "vector", "embedding"}
        t = "double";
    case {"blob", "video", "templateset", "frame"}
        t = "uint8";
    otherwise   % json, string, struct, table, enum, identity, roster
        t = "string";
end
end

% ======================================================================
function key = portKey(compId, portName)
key = sprintf('%s/%s', compId, portName);
end

% ======================================================================
function name = boundaryName(compId, portName)
name = sprintf('%s_%s', strrep(compId, '.', '_'), portName);
end

% ======================================================================
function s = componentSubsystem(spec, compId)
idx = find(strcmp({spec.components.id}, compId), 1);
if isempty(idx)
    error('sihadir:unknownComponent', 'Komponen tidak dikenal: %s', compId);
end
s = spec.components(idx).subsystem;
end

% ======================================================================
function log(fmt, varargin)
fprintf(['  ' fmt '\n'], varargin{:});
end
