function fix_systemcomposer_path(doSave)
%FIX_SYSTEMCOMPOSER_PATH  Register System Composer folders on the MATLAB path.
%
%   The System Composer toolbox files were installed into MATLABROOT, but the
%   installation was interrupted before pathdef.m was regenerated completely.
%   As a result `systemcomposer.createModel` reported
%   "No System Composer installation or license found".
%
%   The authoritative per-component path lists already exist as
%   MATLABROOT/toolbox/local/path/*.phl. This function replays only the
%   System Composer / SysArch entries from those files, so the path ends up
%   exactly as a completed installation would leave it.
%
%   fix_systemcomposer_path()       add the folders and persist the path.
%   fix_systemcomposer_path(false)  add the folders for this session only.
%
%   See also SAVEPATH, BUILD_SIHADIR_ARCHITECTURE.

if nargin < 1
    doSave = true;
end

phlDir = fullfile(matlabroot, 'toolbox', 'local', 'path');
pat = {'*systemcomposer*.phl', '*sysarch*.phl'};
files = {};
for k = 1:numel(pat)
    d = dir(fullfile(phlDir, pat{k}));
    files = [files, {d.name}]; %#ok<AGROW>
end
files = unique(files);

added = {};
missing = {};
for k = 1:numel(files)
    entries = readPhl(fullfile(phlDir, files{k}));
    for e = 1:numel(entries)
        p = fullfile(matlabroot, strrep(entries{e}, '/', filesep));
        if ~isfolder(p)
            missing{end+1} = entries{e}; %#ok<AGROW>
            continue
        end
        if isempty(strfind([path pathsep], [p pathsep])) %#ok<STREMP>
            addpath(p);
            added{end+1} = entries{e}; %#ok<AGROW>
        end
    end
end

fprintf('Folder ditambahkan : %d\n', numel(added));
fprintf('Folder tidak ada   : %d\n', numel(missing));
for k = 1:numel(missing)
    fprintf('  hilang: %s\n', missing{k});
end

if doSave
    try
        savepath;
        fprintf('pathdef.m diperbarui (permanen).\n');
    catch err
        fprintf(2, 'savepath gagal: %s\n', err.message);
        writeStartupFallback(added);
    end
end

ok = ~isempty(which('systemcomposer.createModel'));
fprintf('createModel tersedia: %d\n', ok);
if ~ok
    error('sihadir:path', 'System Composer masih belum dapat dipakai.');
end
end

% ----------------------------------------------------------------------
function entries = readPhl(file)
fid = fopen(file, 'r');
assert(fid > 0, 'Tidak dapat membaca %s', file);
c = onCleanup(@() fclose(fid));
entries = {};
while true
    line = fgetl(fid);
    if ~ischar(line)
        break
    end
    line = strtrim(line);
    if isempty(line) || startsWith(line, '%')
        continue
    end
    entries{end+1} = line; %#ok<AGROW>
end
end

% ----------------------------------------------------------------------
function writeStartupFallback(added)
% No write permission on pathdef.m: persist through startup.m in userpath.
su = fullfile(userpath, 'startup.m');
fid = fopen(su, 'a');
if fid < 0
    fprintf(2, 'Tidak dapat menulis %s\n', su);
    return
end
fprintf(fid, '\n%% System Composer path (ditulis oleh fix_systemcomposer_path)\n');
for k = 1:numel(added)
    fprintf(fid, 'addpath(fullfile(matlabroot, ''%s''));\n', added{k});
end
fclose(fid);
fprintf('Fallback ditulis ke %s\n', su);
end
