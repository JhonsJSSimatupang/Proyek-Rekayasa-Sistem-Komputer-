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

useSC = ~isempty(which('systemcomposer.loadModel'));
if useSC
    model = systemcomposer.loadModel(modelFile);
    arch = model.Architecture;
    subs = arch.Components;
    names = arrayfun(@(s) string(s.Name), subs);
else
    load_system(modelFile);
    spec = sihadir_arch_spec();
    names = strings(1, numel(spec.subsystems));
    for k = 1:numel(spec.subsystems)
        names(k) = sprintf('%s %s', spec.subsystems(k).id, spec.subsystems(k).name);
    end
end

% --------------------------------------------------------- 1. subsystems
nArranged = 0;
for k = 1:numel(names)
    subPath = sprintf('%s/%s', modelName, names(k));
    try
        Simulink.BlockDiagram.arrangeSystem(subPath);
        nArranged = nArranged + 1;
    catch err
        fprintf(2, '  arrange %s gagal: %s\n', names(k), err.message);
    end
end
fprintf('Subsistem di-arrange : %d/%d\n', nArranged, numel(names));

% --------------------------------------------------------------- 2. root
placed = 0;
n = numel(names);
nCols = 3;
nRows = ceil(n / nCols);
cellW = 420;
colGap = 130;
rowGap = 150;
heights = zeros(1, n);
for k = 1:n
    blk = sprintf('%s/%s', modelName, names(k));
    p = get_param(blk, 'Position');
    if useSC
        nPort = numel(subs(k).Ports);
    else
        ph = get_param(blk, 'PortHandles');
        nPort = numel(ph.Inport) + numel(ph.Outport);
    end
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

if useSC
    model.save();
    model.close();
else
    save_system(modelName, modelFile);
    close_system(modelName, 0);
end
end
