function run_sihadir_checks()
%RUN_SIHADIR_CHECKS  Run the whole SiHADIR verification chain and log it.
%
%   Produces S10_evidence.txt in this folder: specification checks,
%   built-model checks and structural counts read back from the saved .slx.
%   This is the transcript quoted in the S10 section of the final report.
%
%   See also VERIFY_ARCHITECTURE_SPEC, VERIFY_BUILT_MODEL,
%   BUILD_SIHADIR_ARCHITECTURE.

here = fileparts(mfilename('fullpath'));
outFile = fullfile(here, 'S10_evidence.txt');
if isfile(outFile)
    delete(outFile);
end
diary(outFile);
diary on;
cleanup = onCleanup(@() diary('off'));

fprintf('=== SiHADIR verification transcript ===\n');
fprintf('MATLAB %s | %s\n', version, datestr(now, 'yyyy-mm-dd HH:MM'));
fprintf('Folder: %s\n\n', here);

% ---------------------------------------------------------------- 1. spec
fprintf('--- 1. Spesifikasi arsitektur ---\n');
spec = sihadir_arch_spec();
repSpec = verify_architecture_spec(spec);
fprintf('Hasil spec: %s (%d/%d)\n\n', passWord(repSpec.pass), ...
    sum([repSpec.checks.pass]), numel(repSpec.checks));

% ---------------------------------------------------------- 2. built model
fprintf('--- 2. Model System Composer ---\n');
repModel = verify_built_model(fullfile(here, 'SiHADIR_Architecture.slx'));

% ------------------------------------------------------ 3. structural proof
fprintf('\n--- 3. Bukti struktur dari berkas .slx ---\n');
modelFile = fullfile(here, 'SiHADIR_Architecture.slx');
[~, modelName] = fileparts(modelFile);
if bdIsLoaded(modelName)
    close_system(modelName, 0);
end
load_system(modelFile);
nLine = numel(find_system(modelName, 'FindAll', 'on', 'Type', 'Line'));
nBlk  = numel(find_system(modelName, 'FindAll', 'on', 'Type', 'Block'));
fprintf('Blok total          : %d\n', nBlk);
fprintf('Garis total         : %d\n', nLine);

useSC = ~isempty(which('systemcomposer.loadModel'));
if useSC
    model = systemcomposer.loadModel(modelFile);
    arch = model.Architecture;
    fprintf('Konektor di root    : %d\n', numel(arch.Connectors));
    subs = arch.Components;
    nSub = 0;
    for k = 1:numel(subs)
        nSub = nSub + numel(subs(k).Architecture.Connectors);
        fprintf('  %-24s port %2d | konektor %2d | komponen %2d\n', ...
            string(subs(k).Name), numel(subs(k).Architecture.Ports), ...
            numel(subs(k).Architecture.Connectors), ...
            numel(subs(k).Architecture.Components));
    end
    fprintf('Konektor di subsistem: %d\n', nSub);
    model.close();
else
    rootLines = find_system(modelName, 'SearchDepth', 1, 'FindAll', 'on', 'Type', 'Line');
    fprintf('Konektor di root    : %d\n', numel(rootLines));
    nSub = 0;
    for k = 1:numel(spec.subsystems)
        sName = sprintf('%s %s', spec.subsystems(k).id, spec.subsystems(k).name);
        sPath = sprintf('%s/%s', modelName, sName);
        pIn  = find_system(sPath, 'SearchDepth', 1, 'BlockType', 'Inport');
        pOut = find_system(sPath, 'SearchDepth', 1, 'BlockType', 'Outport');
        sLines = find_system(sPath, 'SearchDepth', 1, 'FindAll', 'on', 'Type', 'Line');
        sComps = find_system(sPath, 'SearchDepth', 1, 'BlockType', 'SubSystem');
        sComps = setdiff(sComps, {sPath});
        nSub = nSub + numel(sLines);
        fprintf('  %-24s port %2d | konektor %2d | komponen %2d\n', ...
            sName, numel(pIn) + numel(pOut), numel(sLines), numel(sComps));
    end
    fprintf('Konektor di subsistem: %d\n', nSub);
end
close_system(modelName, 0);

% ------------------------------------------------------------- 4. verdict
fprintf('\n--- 4. Kesimpulan ---\n');
fprintf('Spec  : %s\n', passWord(repSpec.pass));
fprintf('Model : %s\n', passWord(repModel.pass));
fprintf('Total : %s\n', passWord(repSpec.pass && repModel.pass));
end

% ======================================================================
function w = passWord(tf)
if tf
    w = 'LULUS';
else
    w = 'GAGAL';
end
end
