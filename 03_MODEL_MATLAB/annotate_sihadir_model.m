function annotate_sihadir_model(modelFile)
%ANNOTATE_SIHADIR_MODEL  Store component identity and function allocation.
%
%   Each component block gets a description of the form
%     ID=C1.3 | jenis=SW | fungsi=F10
%   so the model itself carries the S7 identity and the S8 function
%   allocation instead of keeping that knowledge only in the specification
%   file. System Composer has no Description property on a component, but the
%   component is a Simulink subsystem, and its Description parameter survives
%   save/load and is visible in the block properties.
%
%   annotate_sihadir_model()           annotates SiHADIR_Architecture.slx.
%   annotate_sihadir_model(modelFile)  same, for an explicit model.
%
%   See also BUILD_SIHADIR_ARCHITECTURE, SIHADIR_ARCH_SPEC.

if nargin < 1 || isempty(modelFile)
    modelFile = fullfile(pwd, 'SiHADIR_Architecture.slx');
end
assert(isfile(modelFile), 'Model tidak ditemukan: %s', modelFile);
[~, modelName] = fileparts(modelFile);
if bdIsLoaded(modelName)
    close_system(modelName, 0);
end
load_system(modelName);

spec = sihadir_arch_spec();
nOk = 0;
nFail = 0;
for k = 1:numel(spec.components)
    c = spec.components(k);
    blk = find_system(modelName, 'SearchDepth', 2, 'BlockType', 'SubSystem', ...
        'Name', sprintf('%s %s', c.id, c.name));
    if isempty(blk)
        nFail = nFail + 1;
        continue
    end
    if iscell(blk)
        blk = blk{1};
    end
    desc = sprintf('ID=%s | jenis=%s | fungsi=%s', c.id, c.kind, ...
        strjoin(c.functions, ','));
    try
        set_param(blk, 'Description', desc);
        nOk = nOk + 1;
    catch err
        fprintf(2, '  anotasi %s gagal: %s\n', c.id, err.message);
        nFail = nFail + 1;
    end
end

% Subsystem annotations summarise what each layer contains.
for k = 1:numel(spec.subsystems)
    s = spec.subsystems(k);
    blk = find_system(modelName, 'SearchDepth', 1, 'BlockType', 'SubSystem', ...
        'Name', sprintf('%s %s', s.id, s.name));
    if isempty(blk)
        continue
    end
    if iscell(blk)
        blk = blk{1};
    end
    members = spec.components(strcmp({spec.components.subsystem}, s.id));
    try
        set_param(blk, 'Description', sprintf('Subsistem %s | %d komponen: %s', ...
            s.id, numel(members), strjoin({members.id}, ', ')));
    catch
    end
end

save_system(modelName);
close_system(modelName, 0);
fprintf('Anotasi komponen: %d berhasil, %d gagal\n', nOk, nFail);
end
