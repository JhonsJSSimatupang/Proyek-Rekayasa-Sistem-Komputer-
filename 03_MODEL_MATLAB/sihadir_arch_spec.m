function spec = sihadir_arch_spec()
%SIHADIR_ARCH_SPEC  Single source of truth for the SiHADIR architecture.
%
%   spec = sihadir_arch_spec() returns the physical architecture defined in
%   S7/S8: 6 subsystems, 32 components, their ports, interfaces, links and
%   the function-to-component allocation.
%
%   Both build_sihadir_architecture (System Composer) and
%   verify_architecture_spec (pure MATLAB) consume this file, so the model
%   and the checks can never drift apart.
%
%   See also BUILD_SIHADIR_ARCHITECTURE, VERIFY_ARCHITECTURE_SPEC.

spec          = struct();
spec.name     = 'SiHADIR';
spec.version  = '1.0';
spec.date     = '2026-11-22';

% ---------------------------------------------------------------- subsystems
subData = {
%   id    name
    'S1', 'Edge Terminal'
    'S2', 'Backend Services'
    'S3', 'Integration & Comms'
    'S4', 'Data Management'
    'S5', 'User Interfaces'
    'S6', 'Identity & Privacy'
    };

spec.subsystems = struct('id', {}, 'name', {});
for k = 1:size(subData, 1)
    spec.subsystems(k).id   = subData{k, 1};
    spec.subsystems(k).name = subData{k, 2};
end

% ---------------------------------------------------------------- components
compData = {
%   id      name                              kind     sub   functions
    'C1.1',  'Camera',                        'HW',    'S1',  {'F2.1'}
    'C1.2',  'Compute Unit',                  'HW',    'S1',  {'F2.2','F2.3','F2.4','F2.5','F11'}
    'C1.3',  'Terminal Application',          'SW',    'S1',  {'F3','F10'}
    'C1.4',  'Face Detection & Recognition',  'SW/ML', 'S1',  {'F2.2','F2.4','F2.5'}
    'C1.5',  'Liveness Engine',               'SW/ML', 'S1',  {'F2.3'}
    'C1.6',  'Local Record Store',            'SW',    'S1',  {'F4.2'}
    'C1.7',  'Roster & Template Cache',       'SW',    'S1',  {'F1.1','F2.5'}
    'C1.8',  'Display',                       'HW/SW', 'S1',  {'F10'}
    'C1.9',  'Sync Agent',                    'SW',    'S1',  {'F4.3'}
    'C1.10', 'Time Client',                   'SW',    'S1',  {'F12'}
    'C1.11', 'Readiness Monitor',             'SW',    'S1',  {'F11'}
    'C2.1',  'API Gateway',                   'SW',    'S2',  {'F8.2'}
    'C2.2',  'Session Service',               'SW',    'S2',  {'F1.1','F1.2'}
    'C2.3',  'Attendance Service',            'SW',    'S2',  {'F4.1'}
    'C2.4',  'Rule Engine',                   'SW',    'S2',  {'F3'}
    'C2.5',  'Recap Service',                 'SW',    'S2',  {'F5.1','F5.2'}
    'C2.6',  'Notification Service',          'SW',    'S2',  {'F6.1','F6.2'}
    'C2.7',  'Audit Service',                 'SW',    'S2',  {'F9'}
    'C2.8',  'Access Control Service',        'SW',    'S2',  {'F8.1'}
    'C3.1',  'SIAKAD Connector',              'SW',    'S3',  {'F5.2'}
    'C3.2',  'Notification Connector',        'SW',    'S3',  {'F6.1'}
    'C3.3',  'SSO Connector',                 'SW',    'S3',  {'F8.1'}
    'C4.1',  'Template DB',                   'Data',  'S4',  {'F2.5','F7.2','F7.3'}
    'C4.2',  'Attendance DB',                 'Data',  'S4',  {'F4.1','F5.1'}
    'C4.3',  'Audit Store',                   'Data',  'S4',  {'F7.3','F9'}
    'C4.4',  'Consent Registry',              'Data',  'S4',  {'F7.1'}
    'C5.1',  'Lecturer UI',                   'SW',    'S5',  {'F1.1','F1.2','F10'}
    'C5.2',  'Admin Console',                 'SW',    'S5',  {'F6.2','F7.3'}
    'C5.3',  'Enrolment UI',                  'SW',    'S5',  {'F7.1','F7.2'}
    'C6.1',  'Consent Module',                'SW',    'S6',  {'F7.1'}
    'C6.2',  'Enrolment Module',              'SW',    'S6',  {'F7.2'}
    'C6.3',  'Erasure Module',                'SW',    'S6',  {'F7.3'}
    };

spec.components = struct('id', {}, 'name', {}, 'kind', {}, 'subsystem', {}, 'functions', {});
for k = 1:size(compData, 1)
    spec.components(k).id        = compData{k, 1};
    spec.components(k).name      = compData{k, 2};
    spec.components(k).kind      = compData{k, 3};
    spec.components(k).subsystem = compData{k, 4};
    spec.components(k).functions = compData{k, 5};
end

% ---------------------------------------------------------------- interfaces
ifData = {
%   id          elements
    'IF-T2B',   {'record:json', 'template:blob', 'consent:json'}
    'IF-B2S',   {'recap:json', 'ack:json'}
    'IF-B2SSO', {'authRequest:json', 'token:string'}
    'IF-T2NTP', {'timeQuery:struct', 'timeReply:struct'}
    'IF-B2GW',  {'message:json', 'deliveryStatus:string'}
    'IF-UI2B',  {'command:json', 'query:json', 'view:json'}
    'IF-I1',    {'frame:video'}
    'IF-I2',    {'frame:video', 'embedding:vector'}
    'IF-I3',    {'identity:string', 'score:double'}
    'IF-I4',    {'record:struct', 'display:string'}
    'IF-I5',    {'record:struct'}
    'IF-I6',    {'recap:table'}
    'IF-I7',    {'auditEntry:struct'}
    'IF-I8',    {'status:enum'}
    'IF-I9',    {'roster:table', 'templateSet:blob'}
    'IF-I10',   {'consentProof:struct'}
    };

spec.interfaces = struct('id', {}, 'elements', {});
for k = 1:size(ifData, 1)
    spec.interfaces(k).id       = ifData{k, 1};
    spec.interfaces(k).elements = ifData{k, 2};
end

% ---------------------------------------------------------------- ports
portData = {
%   comp    port            dir     interface
    'C1.1', 'camOut',       'out',  'IF-I1'
    'C1.2', 'statusOut',    'out',  'internal'
    'C1.3', 'camIn',        'in',   'IF-I1'
    'C1.3', 'matchIn',      'in',   'IF-I3'
    'C1.3', 'liveIn',       'in',   'internal'
    'C1.3', 'readyIn',      'in',   'internal'
    'C1.3', 'timeIn',       'in',   'internal'
    'C1.3', 'frameOut',     'out',  'IF-I2'
    'C1.3', 'liveFrameOut', 'out',  'IF-I1'
    'C1.3', 'recordOut',    'out',  'IF-I4'
    'C1.3', 'apiOut',       'out',  'IF-T2B'
    'C1.3', 'displayOut',   'out',  'IF-I4'
    'C1.3', 'enrolOut',     'out',  'IF-T2B'
    'C1.3', 'embedIn',      'in',   'IF-I2'
    'C1.4', 'frameIn',      'in',   'IF-I2'
    'C1.4', 'tplIn',        'in',   'IF-I9'
    'C1.4', 'matchOut',     'out',  'IF-I3'
    'C1.4', 'embedOut',     'out',  'IF-I2'
    'C1.5', 'frameIn',      'in',   'IF-I1'
    'C1.5', 'liveOut',      'out',  'internal'
    'C1.6', 'storeIn',      'in',   'IF-I4'
    'C1.6', 'storeOut',     'out',  'IF-I4'
    'C1.7', 'rosterIn',     'in',   'IF-I9'
    'C1.7', 'tplOut',       'out',  'IF-I9'
    'C1.8', 'dispIn',       'in',   'IF-I4'
    'C1.9', 'syncIn',       'in',   'IF-I4'
    'C1.9', 'syncOut',      'out',  'IF-T2B'
    'C1.10','ntpOut',       'out',  'IF-T2NTP'
    'C1.10','timeOut',      'out',  'internal'
    'C1.11','statusIn',     'in',   'internal'
    'C1.11','readyOut',     'out',  'internal'
    'C2.1', 'termIn',       'in',   'IF-T2B'
    'C2.1', 'syncIn',       'in',   'IF-T2B'
    'C2.1', 'uiIn',         'in',   'IF-UI2B'
    'C2.1', 'uiInAdmin',    'in',   'IF-UI2B'
    'C2.1', 'apiOut',       'out',  'internal'
    'C2.1', 'authIn',       'in',   'internal'
    'C2.1', 'cmdOut',       'out',  'IF-UI2B'
    'C2.1', 'enrolIn',      'in',   'IF-T2B'
    'C2.1', 'enrolOut',     'out',  'IF-T2B'
    'C2.1', 'eraseOut',     'out',  'IF-UI2B'
    'C2.1', 'viewOut',      'out',  'IF-UI2B'
    'C2.1', 'auditOut',     'out',  'IF-I7'
    'C2.1', 'consentIn',    'in',   'IF-I10'
    'C2.1', 'consentOut',   'out',  'IF-I10'
    'C2.2', 'rosterOut',    'out',  'IF-I9'
    'C2.2', 'sessionOut',   'out',  'internal'
    'C2.2', 'cmdIn',        'in',   'IF-UI2B'
    'C2.2', 'tplIn',        'in',   'IF-I9'
    'C2.2', 'timerOut',     'out',  'internal'
    'C2.3', 'recIn',        'in',   'internal'
    'C2.3', 'recOut',       'out',  'IF-I5'
    'C2.3', 'statusIn',     'in',   'IF-I8'
    'C2.3', 'doneOut',      'out',  'internal'
    'C2.3', 'evtOut',       'out',  'internal'
    'C2.3', 'auditOut',     'out',  'IF-I7'
    'C2.4', 'statusOut',    'out',  'IF-I8'
    'C2.4', 'closeIn',      'in',   'internal'
    'C2.5', 'recapIn',      'in',   'IF-I6'
    'C2.5', 'recapOut',     'out',  'IF-B2S'
    'C2.5', 'trigIn',       'in',   'internal'
    'C2.6', 'notifyOut',    'out',  'IF-B2GW'
    'C2.6', 'alertOut',     'out',  'IF-UI2B'
    'C2.6', 'trigIn',       'in',   'internal'
    'C2.6', 'evtIn',        'in',   'internal'
    'C2.6', 'pendingIn',    'in',   'IF-I6'
    'C2.7', 'auditOut',     'out',  'IF-I7'
    'C2.7', 'auditGwIn',    'in',   'IF-I7'
    'C2.7', 'auditAttIn',   'in',   'IF-I7'
    'C2.7', 'auditConsentIn','in',   'IF-I7'
    'C2.7', 'auditEraseIn', 'in',   'IF-I7'
    'C2.8', 'ssoOut',       'out',  'IF-B2SSO'
    'C2.8', 'tokenOut',     'out',  'internal'
    'C3.1', 'recapIn',      'in',   'IF-B2S'
    'C3.1', 'recapOut',     'out',  'IF-B2S'
    'C3.2', 'notifyIn',     'in',   'IF-B2GW'
    'C3.2', 'notifyOut',    'out',  'IF-B2GW'
    'C3.3', 'authIn',       'in',   'IF-B2SSO'
    'C3.3', 'authOut',      'out',  'IF-B2SSO'
    'C4.1', 'tplIn',        'in',   'internal'
    'C4.1', 'tplOut',       'out',  'IF-I9'
    'C4.1', 'tplStoreIn',   'in',   'IF-T2B'
    'C4.2', 'recIn',        'in',   'IF-I5'
    'C4.2', 'recapOut',     'out',  'IF-I6'
    'C4.2', 'pendingOut',   'out',  'IF-I6'
    'C4.3', 'auditIn',      'in',   'IF-I7'
    'C4.4', 'consentIn',    'in',   'IF-I10'
    'C5.1', 'uiOut',        'out',  'IF-UI2B'
    'C5.1', 'viewIn',       'in',   'IF-UI2B'
    'C5.2', 'uiOut',        'out',  'IF-UI2B'
    'C5.2', 'alertIn',      'in',   'IF-UI2B'
    'C5.3', 'consentOut',   'out',  'IF-I10'
    'C6.1', 'consentIn',    'in',   'IF-I10'
    'C6.1', 'consentOut',   'out',  'IF-I10'
    'C6.1', 'auditOut',     'out',  'IF-I7'
    'C6.2', 'tplOut',       'out',  'IF-T2B'
    'C6.2', 'tplIn',        'in',   'IF-T2B'
    'C6.3', 'tplDelOut',    'out',  'internal'
    'C6.3', 'eraseIn',      'in',   'IF-UI2B'
    'C6.3', 'auditOut',     'out',  'IF-I7'
    };

spec.ports = struct('comp', {}, 'name', {}, 'dir', {}, 'interface', {});
for k = 1:size(portData, 1)
    spec.ports(k).comp      = portData{k, 1};
    spec.ports(k).name      = portData{k, 2};
    spec.ports(k).dir       = portData{k, 3};
    spec.ports(k).interface = portData{k, 4};
end

% ---------------------------------------------------------------- links
linkData = {
%   src     srcPort      dst     dstPort       interface
    'C1.1', 'camOut',       'C1.3', 'camIn',        'IF-I1'
    'C1.4', 'matchOut',     'C1.3', 'matchIn',      'IF-I3'
    'C1.5', 'liveOut',      'C1.3', 'liveIn',       'internal'
    'C1.11','readyOut',     'C1.3', 'readyIn',      'internal'
    'C1.3', 'recordOut',    'C1.6', 'storeIn',      'IF-I4'
    'C1.3', 'displayOut',   'C1.8', 'dispIn',       'IF-I4'
    'C1.6', 'storeOut',     'C1.9', 'syncIn',       'IF-I4'
    'C1.3', 'apiOut',       'C2.1', 'termIn',       'IF-T2B'
    'C1.9', 'syncOut',      'C2.1', 'syncIn',       'IF-T2B'
    'C2.2', 'rosterOut',    'C1.7', 'rosterIn',     'IF-I9'
    'C2.3', 'recOut',       'C4.2', 'recIn',        'IF-I5'
    'C4.2', 'recapOut',     'C2.5', 'recapIn',      'IF-I6'
    'C2.5', 'recapOut',     'C3.1', 'recapIn',      'IF-B2S'
    'C2.6', 'notifyOut',    'C3.2', 'notifyIn',     'IF-B2GW'
    'C2.8', 'ssoOut',       'C3.3', 'authIn',       'IF-B2SSO'
    'C2.7', 'auditOut',     'C4.3', 'auditIn',      'IF-I7'
    'C5.1', 'uiOut',        'C2.1', 'uiIn',         'IF-UI2B'
    'C5.2', 'uiOut',        'C2.1', 'uiInAdmin',    'IF-UI2B'
    'C6.1', 'consentOut',   'C4.4', 'consentIn',    'IF-I10'
    'C6.3', 'tplDelOut',    'C4.1', 'tplIn',        'internal'
    'C1.3', 'frameOut',     'C1.4', 'frameIn',      'IF-I2'
    'C1.3', 'liveFrameOut', 'C1.5', 'frameIn',      'IF-I1'
    'C1.7', 'tplOut',       'C1.4', 'tplIn',        'IF-I9'
    'C1.10','timeOut',      'C1.3', 'timeIn',       'internal'
    'C1.2', 'statusOut',    'C1.11','statusIn',     'internal'
    'C1.4', 'embedOut',     'C1.3', 'embedIn',      'IF-I2'
    'C1.3', 'enrolOut',     'C2.1', 'enrolIn',      'IF-T2B'
    'C2.1', 'apiOut',       'C2.3', 'recIn',        'internal'
    'C2.1', 'cmdOut',       'C2.2', 'cmdIn',        'IF-UI2B'
    'C2.8', 'tokenOut',     'C2.1', 'authIn',       'internal'
    'C2.1', 'auditOut',     'C2.7', 'auditGwIn',    'IF-I7'
    'C2.3', 'auditOut',     'C2.7', 'auditAttIn',   'IF-I7'
    'C6.1', 'auditOut',     'C2.7', 'auditConsentIn','IF-I7'
    'C6.3', 'auditOut',     'C2.7', 'auditEraseIn', 'IF-I7'
    'C2.4', 'statusOut',    'C2.3', 'statusIn',     'IF-I8'
    'C2.2', 'sessionOut',   'C2.4', 'closeIn',      'internal'
    'C2.3', 'doneOut',      'C2.5', 'trigIn',       'internal'
    'C2.2', 'timerOut',     'C2.6', 'trigIn',       'internal'
    'C2.3', 'evtOut',       'C2.6', 'evtIn',        'internal'
    'C4.2', 'pendingOut',   'C2.6', 'pendingIn',    'IF-I6'
    'C2.6', 'alertOut',     'C5.2', 'alertIn',      'IF-UI2B'
    'C2.1', 'enrolOut',     'C6.2', 'tplIn',        'IF-T2B'
    'C6.2', 'tplOut',       'C4.1', 'tplStoreIn',   'IF-T2B'
    'C4.1', 'tplOut',       'C2.2', 'tplIn',        'IF-I9'
    'C2.1', 'eraseOut',     'C6.3', 'eraseIn',      'IF-UI2B'
    'C2.1', 'viewOut',      'C5.1', 'viewIn',       'IF-UI2B'
    'C5.3', 'consentOut',   'C2.1', 'consentIn',    'IF-I10'
    'C2.1', 'consentOut',   'C6.1', 'consentIn',    'IF-I10'
    };

spec.links = struct('src', {}, 'srcPort', {}, 'dst', {}, 'dstPort', {}, 'interface', {});
for k = 1:size(linkData, 1)
    spec.links(k).src       = linkData{k, 1};
    spec.links(k).srcPort   = linkData{k, 2};
    spec.links(k).dst       = linkData{k, 3};
    spec.links(k).dstPort   = linkData{k, 4};
    spec.links(k).interface = linkData{k, 5};
end

% ---------------------------------------------------------------- allocation
allocData = {
%   function  component
    'F1.1', 'C2.2'
    'F1.2', 'C2.2'
    'F2.1', 'C1.1'
    'F2.2', 'C1.4'
    'F2.3', 'C1.5'
    'F2.4', 'C1.4'
    'F2.5', 'C1.4'
    'F3',   'C2.4'
    'F4.1', 'C2.3'
    'F4.2', 'C1.6'
    'F4.3', 'C1.9'
    'F5.1', 'C2.5'
    'F5.2', 'C3.1'
    'F6.1', 'C2.6'
    'F6.2', 'C2.6'
    'F7.1', 'C6.1'
    'F7.2', 'C6.2'
    'F7.3', 'C6.3'
    'F8.1', 'C2.8'
    'F8.2', 'C2.1'
    'F9',   'C2.7'
    'F10',  'C1.8'
    'F11',  'C1.11'
    'F12',  'C1.10'
    'F3',   'C1.3'
    };

spec.allocations = struct('function', {}, 'component', {});
for k = 1:size(allocData, 1)
    spec.allocations(k).function  = allocData{k, 1};
    spec.allocations(k).component = allocData{k, 2};
end

spec.requirementsFile = 'RTM_SiHADIR.csv';
end
