function layout_sihadir_model(modelFile)
%LAYOUT_SIHADIR_MODEL  Give the diagram a readable, non-overlapping layout.
%
%   Two findings from this machine drive the implementation:
%
%   1. Simulink.BlockDiagram.arrangeSystem fails with "Memory allocation
%      error" / "call to empty mwboost::function" when it is given the whole
%      model, but works when it is given one subsystem at a time. So each
%      subsystem is arranged on its own.
%
%   2. Setting the position of a component invalidates the handles of its
%      siblings: the first assignment succeeds and every later one fails with
%      "Invalid setting ... for parameter 'Position'". The root level is
%      therefore laid out one component at a time, re-fetching the component
%      from the architecture before each assignment.
%
%   layout_sihadir_model()           lays out SiHADIR_Architecture.slx.
%   layout_sihadir_model(modelFile)  same, for an explicit model.
%
%   See also BUILD_SIHADIR_ARCHITECTURE, RENDER_SIHADIR_MODEL.

if nargin < 1 || isempty(modelFile)
    modelFile = fullfile(pwd, 'SiHADIR_Architecture.slx');
end
assert(isfile(modelFile), 'Model tidak ditemukan: %s', modelFile);
[~, modelName] = fileparts(modelFile);
if bdIsLoaded(modelName)
    close_system(modelName, 0);
end

model = systemcomposer.loadModel(modelFile);
arch = model.Architecture;

% --------------------------------------------------------- 1. subsystems
subs = arch.Components;
names = arrayfun(@(s) string(s.Name), subs);
nArranged = 0;
for k = 1:numel(subs)
    subPath = sprintf('%s/%s', modelName, names(k));
    try
        Simulink.BlockDiagram.arrangeSystem(subPath);
        nArranged = nArranged + 1;
    catch err
        fprintf(2, '  arrange %s gagal: %s\n', names(k), err.message);
    end
end
fprintf('Subsistem di-arrange : %d/%d\n', nArranged, numel(subs));

% --------------------------------------------------------------- 2. root
% The System Composer position setter rejects a height smaller than the one
% the block already needs, which is what made every assignment after the
% first fail. Writing the block parameter directly, and never shrinking the
% height, avoids the check entirely.
% The block path is rebuilt from the model name and the saved component name
% instead of from subs(k).SimulinkHandle, because the handle of a System
% Composer component goes stale as soon as a sibling is moved.
placed = 0;
n = numel(names);
nCols = 3;
nRows = ceil(n / nCols);
cellW = 400;
colGap = 100;
rowGap = 140;
heights = zeros(1, n);
for k = 1:n
    blk = sprintf('%s/%s', modelName, names(k));
    p = get_param(blk, 'Position');
    nPort = numel(subs(k).Ports);
    heights(k) = max([p(4) - p(2), 260, 60 + 18 * nPort]);
end
y = 80;
for r = 1:nRows
    idx = (r - 1) * nCols + (1:nCols);
    idx = idx(idx <= n);
    rowH = max(heights(idx));
    for j = 1:numel(idx)
        k = idx(j);
        blk = sprintf('%s/%s', modelName, names(k));
        x = 80 + (j - 1) * (cellW + colGap);
        try
            set_param(blk, 'Position', [x, y, x + cellW, y + rowH]);
            placed = placed + 1;
        catch err
            fprintf(2, '  posisi root %s gagal: %s\n', names(k), err.message);
        end
    end
    y = y + rowH + rowGap;
end
fprintf('Root ditempatkan     : %d/%d\n', placed, n);

model.save();
model.close();
end
