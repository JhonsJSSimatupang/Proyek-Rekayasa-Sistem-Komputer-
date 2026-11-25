function report = verify_built_model(modelFile)
%VERIFY_BUILT_MODEL  Inspect the generated System Composer model on disk.
%
%   report = verify_built_model() loads SiHADIR_Architecture.slx from the
%   current folder and checks that what was actually written to the model
%   matches SIHADIR_ARCH_SPEC: subsystem count, component count, port count,
%   port direction, port interface and connector count.
%
%   This is the runtime counterpart of VERIFY_ARCHITECTURE_SPEC: that script
%   checks the definition, this one checks the artefact.
%
%   See also SIHADIR_ARCH_SPEC, BUILD_SIHADIR_ARCHITECTURE.

if nargin < 1 || isempty(modelFile)
    modelFile = fullfile(fileparts(mfilename('fullpath')), 'SiHADIR_Architecture.slx');
end
assert(isfile(modelFile), 'Model tidak ditemukan: %s', modelFile);

[~, modelName] = fileparts(modelFile);
if bdIsLoaded(modelName)
    close_system(modelName, 0);
end

spec = sihadir_arch_spec();
checks = struct('id', {}, 'desc', {}, 'pass', {}, 'detail', {});

model = systemcomposer.loadModel(modelFile);
arch  = model.Architecture;

% ---------------------------------------------------------- walk the tree
subs = arch.Components;                 % level 1 = subsystems
leaf = {};
for k = 1:numel(subs)
    kids = subs(k).Architecture.Components;
    for j = 1:numel(kids)
        leaf{end+1} = kids(j); %#ok<AGROW>
    end
end
leafNames = cellfun(@(c) string(c.Name), leaf);

checks = addCheck(checks, 'M1', 'Model dapat dibuka', true, string(modelName));

checks = addCheck(checks, 'M2', 'Jumlah subsistem = 6', numel(subs) == 6, ...
    sprintf('%d subsistem', numel(subs)));

nLeafSpec = numel(spec.components);
checks = addCheck(checks, 'M3', 'Jumlah komponen = 33', numel(leaf) == nLeafSpec, ...
    sprintf('model %d, spec %d', numel(leaf), nLeafSpec));

% ---------------------------------------------------------- ports per comp
% spec names carry an ID prefix, e.g. "C1.1 Edge Face Capture"
specByName = containers.Map('KeyType', 'char', 'ValueType', 'any');
for k = 1:numel(spec.components)
    specByName(sprintf('%s %s', spec.components(k).id, spec.components(k).name)) = spec.components(k).id;
end

nPortModel = 0;
badDir = {};
badIf  = {};
missingComp = {};
for j = 1:numel(leaf)
    cname = char(leafNames(j));
    ports = leaf{j}.Ports;
    nPortModel = nPortModel + numel(ports);
    if ~isKey(specByName, cname)
        missingComp{end+1} = cname; %#ok<AGROW>
        continue
    end
    cid = specByName(cname);
    for p = 1:numel(ports)
        pname = char(string(ports(p).Name));
        idx = find(strcmp({spec.ports.comp}, cid) & strcmp({spec.ports.name}, pname), 1);
        if isempty(idx)
            badDir{end+1} = sprintf('%s/%s tidak ada di spec', cid, pname); %#ok<AGROW>
            continue
        end
        wantDir = spec.ports(idx).dir;
        gotDir  = lower(string(ports(p).Direction));
        if ~isempty(gotDir) && ~startsWith(gotDir, string(wantDir(1)))
            badDir{end+1} = sprintf('%s/%s %s!=%s', cid, pname, gotDir, wantDir); %#ok<AGROW>
        end
        if ~strcmp(spec.ports(idx).interface, 'internal')
            gotIf = readInterfaceName(ports(p));
            wantIf = sihadir_iface_name(spec.ports(idx).interface);
            if ~strcmp(gotIf, wantIf)
                badIf{end+1} = sprintf('%s/%s %s!=%s', cid, pname, gotIf, ...
                    wantIf); %#ok<AGROW>
            end
        end
    end
end

checks = addCheck(checks, 'M4', 'Jumlah port = spec', nPortModel == numel(spec.ports), ...
    sprintf('model %d, spec %d', nPortModel, numel(spec.ports)));

checks = addCheck(checks, 'M5', 'Semua komponen spec ada di model', isempty(missingComp), ...
    sprintf('%d hilang', numel(missingComp)));

checks = addCheck(checks, 'M6', 'Arah port sesuai spec', isempty(badDir), ...
    sprintf('%d menyimpang', numel(badDir)));

checks = addCheck(checks, 'M7', 'Interface port terpasang sesuai spec', isempty(badIf), ...
    sprintf('%d menyimpang', numel(badIf)));

% ---------------------------------------------------------- connectors
nConn = 0;
for k = 1:numel(subs)
    nConn = nConn + numel(subs(k).Architecture.Connectors);
end
checks = addCheck(checks, 'M8', 'Konektor terbentuk (>=22)', nConn >= 22, ...
    sprintf('%d konektor', nConn));

% ---------------------------------------------------------- dictionary
dictPath = fullfile(fileparts(modelFile), [modelName '_Interfaces.sldd']);
dictOk = false;
dictNote = 'tidak ada';
if exist(dictPath, 'file')
    try
        d = systemcomposer.openDictionary(dictPath);
        dictOk = numel(d.Interfaces) >= numel(spec.interfaces);
        dictNote = sprintf('%d interface', numel(d.Interfaces));
    catch err
        dictNote = ['gagal dibuka: ' err.message];
    end
end
checks = addCheck(checks, 'M9', 'Dictionary berisi 16 interface', dictOk, dictNote);

% ---------------------------------------------------------- report
report.checks = checks;
report.pass = all([checks.pass]);
report.counts = struct('subsystems', numel(subs), 'components', numel(leaf), ...
    'ports', nPortModel, 'connectors', nConn);

fprintf('\n=== SiHADIR built-model check ===\n');
fprintf('subsistem %d | komponen %d | port %d | konektor %d\n', ...
    report.counts.subsystems, report.counts.components, ...
    report.counts.ports, report.counts.connectors);
for k = 1:numel(checks)
    if checks(k).pass, flag = 'PASS'; else, flag = 'FAIL'; end
    fprintf('%-4s %-42s %-5s %s\n', checks(k).id, checks(k).desc, flag, checks(k).detail);
end
if report.pass
    fprintf('\nHASIL MODEL: LULUS (%d pemeriksaan)\n', numel(checks));
else
    fprintf('\nHASIL MODEL: GAGAL (%d dari %d)\n', sum(~[checks.pass]), numel(checks));
end

close(model);
end

% ======================================================================
function checks = addCheck(checks, id, desc, pass, detail)
checks(end+1) = struct('id', id, 'desc', desc, 'pass', logical(pass), 'detail', string(detail));
end

function name = readInterfaceName(port)
%READINTERFACENAME  Best-effort read of the interface attached to a port.
name = '';
for prop = {'InterfaceName', 'Interface'}
    try
        v = port.(prop{1});
        if ischar(v) || isstring(v)
            name = char(string(v));
        elseif ~isempty(v)
            name = char(string(v.Name));
        end
        if ~isempty(name)
            return
        end
    catch
    end
end
end
