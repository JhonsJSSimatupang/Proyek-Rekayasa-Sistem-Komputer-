function name = sihadir_iface_name(ifaceId)
%SIHADIR_IFACE_NAME  Dictionary-safe name for a spec interface ID.
%
%   System Composer stores every interface as a MATLAB variable inside the
%   data dictionary, so the name must be a valid MATLAB identifier. The
%   specification and the documents use hyphenated IDs such as "IF-T2B";
%   the dictionary stores "IF_T2B".
%
%   Both BUILD_SIHADIR_ARCHITECTURE and VERIFY_BUILT_MODEL call this
%   function, so the mapping is defined once and cannot drift.
%
%   See also SIHADIR_ARCH_SPEC, BUILD_SIHADIR_ARCHITECTURE.

name = char(regexprep(char(string(ifaceId)), '[^A-Za-z0-9_]', '_'));
if ~isletter(name(1))
    name = ['IF_' name];
end
end
