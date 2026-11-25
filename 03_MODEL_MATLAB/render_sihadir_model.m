function render_sihadir_model(modelFile, pngDir)
%RENDER_SIHADIR_MODEL  Tidy the diagram layout and export PNG snapshots.
%
%   render_sihadir_model()            lays out SiHADIR_Architecture.slx and
%                                     writes SiHADIR_root.png next to it.
%   render_sihadir_model(modelFile)   same, for an explicit model.
%   render_sihadir_model(modelFile, pngDir)
%                                     also writes one PNG per subsystem into
%                                     pngDir (created when absent).
%
%   The layout pass matters for the report: without it the auto-placed blocks
%   overlap and the connectors are unreadable even though they exist.
%
%   See also BUILD_SIHADIR_ARCHITECTURE, WIRE_SIHADIR_MODEL.

if nargin < 1 || isempty(modelFile)
    modelFile = fullfile(pwd, 'SiHADIR_Architecture.slx');
end
if nargin < 2 || isempty(pngDir)
    pngDir = fileparts(modelFile);
end
assert(isfile(modelFile), 'Model tidak ditemukan: %s', modelFile);
if ~isfolder(pngDir)
    mkdir(pngDir);
end

[~, modelName] = fileparts(modelFile);
if bdIsLoaded(modelName)
    close_system(modelName, 0);
end
load_system(modelName);

% ---------------------------------------------------------------- layout
% arrangeSystem is unusable on this machine (memory allocation error), so the
% deterministic grid in LAYOUT_SIHADIR_MODEL is used instead.
close_system(modelName, 0);
layout_sihadir_model(modelFile);
load_system(modelName);

subs = find_system(modelName, 'SearchDepth', 1, 'BlockType', 'SubSystem');
save_system(modelName);
fprintf('Layout dirapikan: root + %d subsistem\n', numel(subs));

% ------------------------------------------------------------------ png
rootPng = fullfile(pngDir, 'SiHADIR_root.png');
okRoot = tryPrint(modelName, rootPng);
fprintf('PNG root          : %s\n', status(okRoot, rootPng));

nSub = 0;
for k = 1:numel(subs)
    [~, leaf] = fileparts(subs{k});
    leaf = regexprep(leaf, '[^A-Za-z0-9]+', '_');
    p = fullfile(pngDir, ['SiHADIR_' leaf '.png']);
    if tryPrint(subs{k}, p)
        nSub = nSub + 1;
    end
end
fprintf('PNG subsistem     : %d/%d\n', nSub, numel(subs));

close_system(modelName, 0);
end

% ======================================================================
function ok = tryPrint(sysPath, pngPath)
ok = false;
try
    print(['-s' sysPath], '-dpng', '-r120', pngPath);
    ok = isfile(pngPath);
catch err
    fprintf(2, '  ekspor gagal pada %s: %s\n', sysPath, err.message);
end
end

% ======================================================================
function s = status(ok, pngPath)
if ok
    d = dir(pngPath);
    s = sprintf('OK (%d byte)', d.bytes);
else
    s = 'GAGAL';
end
end
