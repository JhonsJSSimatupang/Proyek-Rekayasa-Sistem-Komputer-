function report = verify_architecture_spec(spec, rtmFile)
%VERIFY_ARCHITECTURE_SPEC  Check the SiHADIR architecture definition.
%
%   report = verify_architecture_spec(spec) checks internal consistency of
%   the spec returned by SIHADIR_ARCH_SPEC and cross-checks the function
%   allocation against RTM_SiHADIR.csv.
%
%   report = verify_architecture_spec(spec, rtmFile) uses an explicit RTM
%   path. Pass '' to skip the RTM cross-check.
%
%   report.pass is true when no check failed.
%
%   See also SIHADIR_ARCH_SPEC, BUILD_SIHADIR_ARCHITECTURE.

if nargin < 2 || isempty(rtmFile)
    hereDir = fileparts(mfilename('fullpath'));
    rtmFile = fullfile(hereDir, 'RTM_SiHADIR.csv');
    if ~exist(rtmFile, 'file')
        rtmFile = fullfile(hereDir, '..', '02_DOKUMENTASI_SUMBER', 'RTM_SiHADIR.csv');
    end
end

checks = struct('id', {}, 'desc', {}, 'pass', {}, 'detail', {});

compIds = {spec.components.id};
portKey = arrayfun(@(p) [p.comp '/' p.name], spec.ports, 'UniformOutput', false);
ifIds   = {spec.interfaces.id};
subIds  = {spec.subsystems.id};

% --- C1 unique component ids
[~, ia] = unique(compIds);
checks = addCheck(checks, 'C1', 'ID komponen unik', numel(ia) == numel(compIds), ...
    sprintf('%d komponen', numel(compIds)));

% --- C2 unique (component, port)
[~, ib] = unique(portKey);
checks = addCheck(checks, 'C2', 'Pasangan komponen/port unik', numel(ib) == numel(portKey), ...
    sprintf('%d port', numel(portKey)));

% --- C3 every port belongs to a known component
bad = portKey(~ismember({spec.ports.comp}, compIds));
checks = addCheck(checks, 'C3', 'Port menempel pada komponen yang ada', isempty(bad), ...
    sprintf('%d pelanggaran', numel(bad)));

% --- C4 every port interface is declared
ifaceOfPort = {spec.ports.interface};
bad = setdiff(unique(ifaceOfPort), [ifIds, {'internal'}]);
checks = addCheck(checks, 'C4', 'Interface port terdeklarasi', isempty(bad), ...
    sprintf('tidak dikenal: %s', strjoin(bad, ', ')));

% --- C5 every component owns at least one port
noPort = compIds(~ismember(compIds, {spec.ports.comp}));
checks = addCheck(checks, 'C5', 'Setiap komponen punya minimal satu port', isempty(noPort), ...
    sprintf('tanpa port: %s', strjoin(noPort, ', ')));

% --- C6 every subsystem owns at least one component
subOfComp = {spec.components.subsystem};
emptySub = subIds(~ismember(subIds, subOfComp));
checks = addCheck(checks, 'C6', 'Setiap subsistem berisi komponen', isempty(emptySub), ...
    sprintf('kosong: %s', strjoin(emptySub, ', ')));

% --- C7 link endpoints exist
missing = {};
for k = 1:numel(spec.links)
    if ~any(strcmp(portKey, [spec.links(k).src '/' spec.links(k).srcPort]))
        missing{end+1} = [spec.links(k).src '/' spec.links(k).srcPort]; %#ok<AGROW>
    end
    if ~any(strcmp(portKey, [spec.links(k).dst '/' spec.links(k).dstPort]))
        missing{end+1} = [spec.links(k).dst '/' spec.links(k).dstPort]; %#ok<AGROW>
    end
end
checks = addCheck(checks, 'C7', 'Ujung link menunjuk port yang ada', isempty(missing), ...
    sprintf('hilang: %s', strjoin(missing, ', ')));

% --- C8 link direction is out -> in
badDir = {};
for k = 1:numel(spec.links)
    s = getPortDir(spec, spec.links(k).src, spec.links(k).srcPort);
    d = getPortDir(spec, spec.links(k).dst, spec.links(k).dstPort);
    if ~(strcmp(s, 'out') && strcmp(d, 'in'))
        badDir{end+1} = sprintf('%s(%s)->%s(%s)', spec.links(k).src, s, ...
            spec.links(k).dst, d); %#ok<AGROW>
    end
end
checks = addCheck(checks, 'C8', 'Arah link out -> in', isempty(badDir), ...
    sprintf('%d salah arah', numel(badDir)));

% --- C9 link interface matches both ports
badIf = {};
for k = 1:numel(spec.links)
    l = spec.links(k);
    si = getPortIface(spec, l.src, l.srcPort);
    di = getPortIface(spec, l.dst, l.dstPort);
    if ~(strcmp(si, l.interface) && strcmp(di, l.interface))
        badIf{end+1} = sprintf('%s->%s', l.src, l.dst); %#ok<AGROW>
    end
end
checks = addCheck(checks, 'C9', 'Interface link konsisten dengan port', isempty(badIf), ...
    sprintf('%d tidak konsisten', numel(badIf)));

% --- C10 allocation points at existing components
allocComp = {spec.allocations.component};
badAlloc = allocComp(~ismember(allocComp, compIds));
checks = addCheck(checks, 'C10', 'Alokasi fungsi menunjuk komponen yang ada', isempty(badAlloc), ...
    sprintf('tidak dikenal: %s', strjoin(badAlloc, ', ')));

% --- C11 every function owned by a component is allocated
owned = {};
for k = 1:numel(spec.components)
    owned = [owned, spec.components(k).functions]; %#ok<AGROW>
end
allocFn = {spec.allocations.function};
notAllocated = setdiff(unique(owned), allocFn);
checks = addCheck(checks, 'C11', 'Fungsi yang dimiliki komponen teralokasi', isempty(notAllocated), ...
    sprintf('belum: %s', strjoin(notAllocated, ', ')));

% --- C12 allocation target really owns that function
badOwner = {};
for k = 1:numel(spec.allocations)
    a = spec.allocations(k);
    idx = find(strcmp(compIds, a.component), 1);
    if isempty(idx) || ~any(strcmp(spec.components(idx).functions, a.function))
        badOwner{end+1} = sprintf('%s->%s', a.function, a.component); %#ok<AGROW>
    end
end
checks = addCheck(checks, 'C12', 'Komponen tujuan benar-benar memiliki fungsi', isempty(badOwner), ...
    sprintf('%d menyimpang', numel(badOwner)));

% --- C13 interface declared but never used (warning only)
usedIf = unique(ifaceOfPort);
unused = setdiff(ifIds, usedIf);
checks = addCheck(checks, 'C13', 'Interface terpakai (peringatan)', isempty(unused), ...
    sprintf('belum dipakai: %s', strjoin(unused, ', ')));

% --- C14 RTM function coverage
rtmNote = 'dilewati';
if ~isempty(rtmFile) && exist(rtmFile, 'file')
    try
        T = readtable(rtmFile, 'TextType', 'string', 'Delimiter', ',');
        fnCol = T.("Function");
        rtmFn = strings(0, 1);
        for k = 1:numel(fnCol)
            parts = split(fnCol(k), ';');
            rtmFn = [rtmFn; strtrim(parts(:))]; %#ok<AGROW>
        end
        rtmFn = unique(rtmFn(rtmFn ~= ""));
        rtmFn = setdiff(rtmFn, ["F2", "F4"]);          % aggregate nodes
        miss = setdiff(rtmFn, allocFn);
        checks = addCheck(checks, 'C14', 'Semua fungsi di RTM punya komponen', isempty(miss), ...
            sprintf('%d dari %d fungsi belum dialokasikan', numel(miss), numel(rtmFn)));
        rtmNote = sprintf('%d fungsi RTM', numel(rtmFn));
    catch err
        checks = addCheck(checks, 'C14', 'Semua fungsi di RTM punya komponen', false, ...
            ['gagal membaca RTM: ' err.message]);
        rtmNote = 'gagal';
    end
else
    checks = addCheck(checks, 'C14', 'Semua fungsi di RTM punya komponen', true, 'RTM tidak ditemukan, dilewati');
end

% --- C15 no dangling interface in links
checks = addCheck(checks, 'C15', 'Interface pada link terdeklarasi', ...
    all(ismember(unique({spec.links.interface}), [ifIds, {'internal'}])), ...
    sprintf('%d link', numel(spec.links)));

% ---------------------------------------------------------------- report
report.checks = checks;
report.pass   = all([checks.pass]);
report.failed = {checks(~[checks.pass]).id};
report.counts = struct( ...
    'components', numel(compIds), ...
    'ports',      numel(portKey), ...
    'interfaces', numel(ifIds), ...
    'links',      numel(spec.links), ...
    'allocations',numel(spec.allocations), ...
    'rtm',        rtmNote);

fprintf('\n=== SiHADIR architecture check ===\n');
fprintf('komponen %d | port %d | interface %d | link %d | alokasi %d | %s\n', ...
    report.counts.components, report.counts.ports, report.counts.interfaces, ...
    report.counts.links, report.counts.allocations, report.counts.rtm);
fprintf('%-4s %-52s %-5s %s\n', 'ID', 'Pemeriksaan', 'Hasil', 'Detail');
for k = 1:numel(checks)
    if checks(k).pass
        flag = 'PASS';
    else
        flag = 'FAIL';
    end
    fprintf('%-4s %-52s %-5s %s\n', checks(k).id, checks(k).desc, flag, checks(k).detail);
end

nFail = sum(~[checks.pass]);
if nFail == 0
    fprintf('\nHASIL: LULUS (%d pemeriksaan)\n', numel(checks));
else
    fprintf('\nHASIL: GAGAL (%d dari %d pemeriksaan)\n', nFail, numel(checks));
end
end

% ======================================================================
function checks = addCheck(checks, id, desc, pass, detail)
checks(end+1) = struct('id', id, 'desc', desc, 'pass', logical(pass), 'detail', detail);
end

function d = getPortDir(spec, comp, port)
idx = find(strcmp({spec.ports.comp}, comp) & strcmp({spec.ports.name}, port), 1);
if isempty(idx)
    d = '?';
else
    d = spec.ports(idx).dir;
end
end

function i = getPortIface(spec, comp, port)
idx = find(strcmp({spec.ports.comp}, comp) & strcmp({spec.ports.name}, port), 1);
if isempty(idx)
    i = '?';
else
    i = spec.ports(idx).interface;
end
end
