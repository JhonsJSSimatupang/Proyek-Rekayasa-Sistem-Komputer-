function report = verify_built_model(modelFile)
%VERIFY_BUILT_MODEL  Inspect the generated System Composer / Simulink model on disk.
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

useSC = ~isempty(which('systemcomposer.loadModel'));
if useSC
    model = systemcomposer.loadModel(modelFile);
    arch  = model.Architecture;
    subs = arch.Components;                 % level 1 = subsystems
    leaf = {};
    for k = 1:numel(subs)
        kids = subs(k).Architecture.Components;
        for j = 1:numel(kids)
            leaf{end+1} = kids(j); %#ok<AGROW>
        end
    end
    leafNames = cellfun(@(c) string(c.Name), leaf);
    nSubs = numel(subs);
    nLeaf = numel(leaf);
else
    load_system(modelFile);
    subBlks = find_system(modelName, 'SearchDepth', 1, 'BlockType', 'SubSystem');
    nSubs = numel(subBlks);
    leafBlks = {};
    for k = 1:nSubs
        kids = find_system(subBlks{k}, 'SearchDepth', 1, 'BlockType', 'SubSystem');
        kids = setdiff(kids, subBlks(k), 'stable');
        leafBlks = [leafBlks; kids(:)]; %#ok<AGROW>
    end
    nLeaf = numel(leafBlks);
    leafNames = cellfun(@(b) string(get_param(b, 'Name')), leafBlks);
end

checks = addCheck(checks, 'M1', 'Model dapat dibuka', true, string(modelName));

checks = addCheck(checks, 'M2', 'Jumlah subsistem = 6', nSubs == 6, ...
    sprintf('%d subsistem', nSubs));

nLeafSpec = numel(spec.components);
checks = addCheck(checks, 'M3', sprintf('Jumlah komponen = %d', nLeafSpec), nLeaf == nLeafSpec, ...
    sprintf('model %d, spec %d', nLeaf, nLeafSpec));

% ---------------------------------------------------------- ports per comp
specByName = containers.Map('KeyType', 'char', 'ValueType', 'any');
for k = 1:numel(spec.components)
    specByName(sprintf('%s %s', spec.components(k).id, spec.components(k).name)) = spec.components(k).id;
end

nPortModel = 0;
badDir = {};
badIf  = {};
missingComp = {};

if useSC
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
else
    for j = 1:numel(leafBlks)
        cname = char(leafNames(j));
        cBlk = leafBlks{j};
        pIn  = find_system(cBlk, 'SearchDepth', 1, 'BlockType', 'Inport');
        pOut = find_system(cBlk, 'SearchDepth', 1, 'BlockType', 'Outport');
        allP = [pIn(:); pOut(:)];
        nPortModel = nPortModel + numel(allP);
        if ~isKey(specByName, cname)
            missingComp{end+1} = cname; %#ok<AGROW>
            continue
        end
        cid = specByName(cname);
        for p = 1:numel(allP)
            pBlk = allP{p};
            try
                pname = get_param(pBlk, 'PortName');
            catch
                pname = get_param(pBlk, 'Name');
            end
            idx = find(strcmp({spec.ports.comp}, cid) & strcmp({spec.ports.name}, pname), 1);
            if isempty(idx)
                badDir{end+1} = sprintf('%s/%s tidak ada di spec', cid, pname); %#ok<AGROW>
                continue
            end
            wantDir = spec.ports(idx).dir;
            bType = get_param(pBlk, 'BlockType');
            if strcmp(bType, 'Inport'), gotDir = 'in'; else, gotDir = 'out'; end
            if ~strcmp(gotDir, wantDir)
                badDir{end+1} = sprintf('%s/%s %s!=%s', cid, pname, gotDir, wantDir); %#ok<AGROW>
            end
            if ~strcmp(spec.ports(idx).interface, 'internal')
                wantIf = sihadir_iface_name(spec.ports(idx).interface);
                dt = get_param(pBlk, 'OutDataTypeStr');
                gotIf = strtrim(strrep(dt, 'Bus:', ''));
                if ~isempty(gotIf) && ~strcmp(gotIf, 'Inherit: auto') && ~strcmp(gotIf, wantIf)
                    badIf{end+1} = sprintf('%s/%s %s!=%s', cid, pname, gotIf, wantIf); %#ok<AGROW>
                end
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
if useSC
    for k = 1:numel(subs)
        nConn = nConn + numel(subs(k).Architecture.Connectors);
    end
else
    for k = 1:numel(subBlks)
        lines = find_system(subBlks{k}, 'SearchDepth', 1, 'FindAll', 'on', 'Type', 'Line');
        nConn = nConn + numel(lines);
    end
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
report.counts = struct('subsystems', nSubs, 'components', nLeaf, ...
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

if useSC
    close(model);
else
    close_system(modelName, 0);
end
end

% ======================================================================
function checks = addCheck(checks, id, desc, pass, detail)
checks(end+1) = struct('id', id, 'desc', desc, 'pass', logical(pass), 'detail', string(detail));
end

function name = readInterfaceName(port)
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
