!define APPNAME "jdMinecraftLauncher"
!define APPBIN "$INSTDIR\${APPNAME}.exe"

Name "${APPNAME}"
OutFile "${APPNAME}Installer.exe"
ManifestDPIAware true
Unicode True

SetCompressor /SOLID lzma

!include "FileFunc.nsh"
!include "LogicLib.nsh"
!include "x64.nsh"

!define MULTIUSER_USE_PROGRAMFILES64
!define MULTIUSER_INSTALLMODE_INSTDIR "$(^Name)"
!define MULTIUSER_INSTALLMODE_COMMANDLINE
!define MULTIUSER_EXECUTIONLEVEL Highest
!define MULTIUSER_INSTALLMODE_INSTDIR_REGISTRY_KEY "Software\JakobDev\${APPNAME}"
!define MULTIUSER_INSTALLMODE_INSTDIR_REGISTRY_VALUENAME "Installdir"
!define MULTIUSER_INSTALLMODE_DEFAULT_REGISTRY_KEY "Software\JakobDev\${APPNAME}"
!define MULTIUSER_INSTALLMODE_DEFAULT_REGISTRY_VALUENAME "MultiUserInstallmode"
!define MULTIUSER_MUI

!include "MultiUser.nsh"
!include "MUI2.nsh"

;RequestExecutionLevel highest

!define MUI_ABORTWARNING

!define MUI_ICON "Icon.ico"
!define MUI_UNICON "Icon.ico"
!define MUI_FINISHPAGE_RUN "${APPBIN}"

;Installer Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MULTIUSER_PAGE_INSTALLMODE
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

;Languages
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "German"

;Get the current version
!define /file VERSION "..\${APPNAME}\version.txt"

Function .onInit
    ${IfNot} ${RunningX64}
        Abort
    ${EndIf}

    ${DisableX64FSRedirection}
    SetRegView 64

    !insertmacro MULTIUSER_INIT
FunctionEnd

Function un.onInit
    ${IfNot} ${RunningX64}
        Abort
    ${EndIf}

    ${DisableX64FSRedirection}
    SetRegView 64

    !insertmacro MULTIUSER_UNINIT
FunctionEnd

Section
    RMDir /r "$INSTDIR"
    SetOutPath "$INSTDIR"
    File /r ..\WindowsBuild\Portable\*

    CreateShortcut "$SMPROGRAMS\${APPNAME}.lnk" "${APPBIN}"

    ; Write the installation path into the registry
    WriteRegStr SHCTX "Software\JakobDev\${APPNAME}" "${MULTIUSER_INSTALLMODE_INSTDIR_REGISTRY_VALUENAME}" "$INSTDIR"
    WriteRegStr SHCTX "Software\JakobDev\${APPNAME}" "${MULTIUSER_INSTALLMODE_DEFAULT_REGISTRY_VALUENAME}" "$MultiUser.InstallMode"

    ; Let the App appear in the uninstall menu (https://nsis.sourceforge.io/Add_uninstall_information_to_Add/Remove_Programs)
    WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
    WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "QuietUninstallString" "$\"$INSTDIR\Uninstall.exe$\" /S"
    WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$\"${APPBIN}$\""
    WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation" "$\"$INSTDIR$\""
    WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSION}"
    WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "JakobDev"
    WriteRegDWORD SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoModify" 1
    WriteRegDWORD SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoRepair" 1

    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "EstimatedSize" "$0"

    WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Uninstall"
    RMDir /r "$INSTDIR"

    Delete "$SMPROGRAMS\${APPNAME}.lnk"

    DeleteRegKey SHCTX "Software\JakobDev\${APPNAME}"
    DeleteRegKey /ifempty SHCTX "Software\JakobDev"
    DeleteRegKey SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
SectionEnd
