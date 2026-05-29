#define AppVersion GetEnv("CPHO_APP_VERSION")
#if AppVersion == ""
  #define AppVersion "0.1.0"
#endif

#define SourceDir GetEnv("CPHO_DIST_DIR")
#if SourceDir == ""
  #define SourceDir "..\dist\cpho"
#endif

#define InstallerOutputDir GetEnv("CPHO_INSTALLER_OUTPUT_DIR")
#if InstallerOutputDir == ""
  #define InstallerOutputDir "..\dist\installer"
#endif

[Setup]
AppId={{FA35D82C-6928-41FD-9C61-26F555DD276D}
AppName=CPHO CLI
AppVersion={#AppVersion}
AppPublisher=CPHO CLI
AppPublisherURL=https://github.com/zyzericzhang/cpho-cli
AppSupportURL=https://github.com/zyzericzhang/cpho-cli/issues
AppUpdatesURL=https://github.com/zyzericzhang/cpho-cli/releases/latest
DefaultDirName={autopf}\CPHO CLI
DefaultGroupName=CPHO CLI
DisableProgramGroupPage=yes
OutputDir={#InstallerOutputDir}
OutputBaseFilename=cpho-cli-{#AppVersion}-windows-x64-setup
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=lowest
WizardStyle=modern

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\CPHO CLI"; Filename: "{app}\cpho.exe"; WorkingDir: "{app}"
