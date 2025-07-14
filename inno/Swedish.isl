; *** Inno Setup version 6.4.0+ Swedish messages ***
;
; To download user-contributed translations of this file, go to:
;   http://www.jrsoftware.org/files/istrans/
;
; Note: When translating this text, do not add periods (.) to the end of
; messages that didn't have them already, because on those messages Inno
; Setup adds the periods automatically (appending a period would result in
; two periods being displayed).
;
; Translated by stefan@bodingh.se (Stefan Bodingh)
; Reviewed and updated by info@danielnylander.se (Daniel Nylander)
;

; The following three entries are very important. Be sure to read and
; understand the '[LangOptions] section' topic in the help file.


[LangOptions]
LanguageName=Svenska
LanguageID=$041D
LanguageCodePage=1252
; If the language you are translating to requires special font faces or
; sizes, uncomment any of the following entries and change them accordingly.
;DialogFontName=
;DialogFontSize=8
;WelcomeFontName=Verdana
;WelcomeFontSize=12
;TitleFontName=Arial
;TitleFontSize=29
;CopyrightFontName=Arial
;CopyrightFontSize=8


; *** Application titles


[Messages]
SetupAppTitle=Installationsprogram
SetupWindowTitle=Installationsprogram f�r %1
UninstallAppTitle=Avinstallation
UninstallAppFullTitle=%1 Avinstallation

; *** Misc. common
InformationTitle=Information
ConfirmTitle=Bekr�fta
ErrorTitle=Fel

; *** SetupLdr messages
SetupLdrStartupMessage=%1 kommer att installeras. Vill du forts�tta?
LdrCannotCreateTemp=Kan inte skapa en tempor�rfil. Installationen avbryts
LdrCannotExecTemp=Kan inte k�ra fil i tempor�rkatalogen. Installationen avbryts
HelpTextNote=

; *** Startup error messages
LastErrorMessage=%1.%n%nFel %2: %3
SetupFileMissing=Filen %1 saknas i installationskatalogen. R�tta till problemet eller h�mta en ny kopia av programmet.
SetupFileCorrupt=Installationsfilerna �r skadade. H�mta en ny kopia av programmet.
SetupFileCorruptOrWrongVer=Installationsfilerna �r skadade, eller st�mmer inte �verens med denna version av installationsprogrammet. R�tta till felet eller h�mta en ny programkopia.
InvalidParameter=En ogiltig parameter angavs p� kommandoraden:%n%n%1
SetupAlreadyRunning=Installationsprogrammet k�rs redan.
WindowsVersionNotSupported=Detta program saknar st�d f�r den version av Windows som k�rs p� datorn.
WindowsServicePackRequired=Detta program kr�ver %1 Service Pack %2 eller senare.
NotOnThisPlatform=Detta program kan inte k�ras p� %1.
OnlyOnThisPlatform=Detta program m�ste k�ras p� %1.
OnlyOnTheseArchitectures=Detta program kan bara installeras p� Windows-versioner med f�ljande processorarkitekturer:%n%n%1
WinVersionTooLowError=Detta program kr�ver %1 version %2 eller senare.
WinVersionTooHighError=Detta program kan inte installeras p� %1 version %2 eller senare.
AdminPrivilegesRequired=Du m�ste vara inloggad som administrat�r n�r du installerar detta program.
PowerUserPrivilegesRequired=Du m�ste vara inloggad som administrat�r eller medlem av gruppen Privilegierade anv�ndare (Power Users) n�r du installerar detta program.
SetupAppRunningError=Installationsprogrammet har uppt�ckt att %1 �r ig�ng.%n%nAvsluta det angivna programmet nu. Klicka sedan p� OK f�r att g� vidare eller p� Avbryt f�r att avsluta.
UninstallAppRunningError=Avinstalleraren har uppt�ckt att %1 k�rs f�r tillf�llet.%n%nSt�ng all �ppna instanser av det nu, klicka sedan p� OK f�r att g� vidare eller p� Avbryt f�r att avsluta.

; *** Startup questions
PrivilegesRequiredOverrideTitle=V�lj installationstyp
PrivilegesRequiredOverrideInstruction=V�lj installationstyp
PrivilegesRequiredOverrideText1=%1 kan installeras f�r alla anv�ndare (kr�ver administrat�rsbeh�righet) eller bara f�r dig.
PrivilegesRequiredOverrideText2=%1 kan installeras bara f�r dig eller f�r alla anv�ndare (kr�ver administrat�rsbeh�righet).
PrivilegesRequiredOverrideAllUsers=Installera f�r &alla anv�ndare
PrivilegesRequiredOverrideAllUsersRecommended=Installera f�r &alla anv�ndare (rekommenderas)
PrivilegesRequiredOverrideCurrentUser=Installera f�r &mig enbart
PrivilegesRequiredOverrideCurrentUserRecommended=Installera f�r &mig enbart (rekommenderas)

; *** Misc. errors
ErrorCreatingDir=Installationsprogrammet kunde inte skapa katalogen "%1"
ErrorTooManyFilesInDir=Kunde inte skapa en fil i katalogen "%1" d�rf�r att den inneh�ller f�r m�nga filer

; *** Setup common messages
ExitSetupTitle=Avsluta installationen
ExitSetupMessage=Installationen �r inte f�rdig. Om du avslutar nu s� kommer programmet inte att installeras.%n%nDu kan k�ra installationsprogrammet vid ett senare tillf�lle f�r att slutf�ra installationen.%n%nVill du avbryta installationen?
AboutSetupMenuItem=&Om installationsprogrammet...
AboutSetupTitle=Om installationsprogrammet
AboutSetupMessage=%1 version %2%n%3%n%n%1 webbsida:%n%4
AboutSetupNote=Svensk �vers�ttning �r gjord av dickg@go.to 1999, 2002%n%nUppdatering till 3.0.2+ av peter@peterandlinda.com, 4.+ av stefan@bodingh.se, 6.4+ info@danielnylander.se
TranslatorNote=

; *** Buttons
ButtonBack=< &Tillbaka
ButtonNext=&N�sta >
ButtonInstall=&Installera
ButtonOK=Ok
ButtonCancel=Avbryt
ButtonYes=&Ja
ButtonYesToAll=Ja till &allt
ButtonNo=&Nej
ButtonNoToAll=N&ej till allt
ButtonFinish=&Slutf�r
ButtonBrowse=&Bl�ddra...
ButtonWizardBrowse=Bl�&ddra...
ButtonNewFolder=Skapa ny mapp

; *** "Select Language" dialog messages
SelectLanguageTitle=V�lj spr�k f�r installationen
SelectLanguageLabel=V�lj det spr�k som skall anv�ndas under installationen.

; *** Common wizard text
ClickNext=Klicka p� N�sta f�r att forts�tta eller p� Avbryt f�r att avsluta installationen.
BeveledLabel=
BrowseDialogTitle=V�lj mapp
BrowseDialogLabel=V�lj en mapp i listan nedan, klicka sedan p� OK.
NewFolderName=Ny mapp

; *** "Welcome" wizard page
WelcomeLabel1=V�lkommen till installationsprogrammet f�r [name].
WelcomeLabel2=Detta kommer att installera [name/ver] p� din dator.%n%nDet rekommenderas att du avslutar alla andra program innan du forts�tter.

; *** "License Agreement" wizard page
WizardLicense=Licensavtal
LicenseLabel=L�s igenom f�ljande viktiga information innan du forts�tter.
LicenseLabel3=L�s igenom f�ljande licensavtal. Du m�ste acceptera villkoren i avtalet innan du kan forts�tta med installationen.
LicenseAccepted=Jag &accepterar avtalet
LicenseNotAccepted=Jag accepterar &inte avtalet

; *** "Information" wizard pages
WizardInfoBefore=Information
InfoBeforeLabel=L�s igenom f�ljande viktiga information innan du forts�tter.
InfoBeforeClickLabel=Klicka p� N�sta n�r du �r klar att forts�tta med installationen.
WizardInfoAfter=Information
InfoAfterLabel=L�s igenom f�ljande viktiga information innan du forts�tter.
InfoAfterClickLabel=Klicka p� N�sta n�r du �r klar att forts�tta med installationen.

; *** "User Information" wizard page
WizardUserInfo=Anv�ndarinformation
UserInfoDesc=Fyll i f�ljande uppgifter.
UserInfoName=&Namn:
UserInfoOrg=&Organisation:
UserInfoSerial=&Serienummer:
UserInfoNameRequired=Du m�ste fylla i ett namn.

; *** "Select Destination Directory" wizard page
WizardSelectDir=V�lj installationsplats
SelectDirDesc=Var skall [name] installeras?
SelectDirLabel3=Installationsprogrammet kommer att installera [name] i f�ljande mapp
SelectDirBrowseLabel=F�r att forts�tta klickar du p� N�sta. Om du vill v�lja en annan mapp s� klickar du p� Bl�ddra.
DiskSpaceGBLabel=Programmet kr�ver minst [gb] GB h�rddiskutrymme.
DiskSpaceMBLabel=Programmet kr�ver minst [mb] MB h�rddiskutrymme.
CannotInstallToNetworkDrive=Installationsprogrammet kan inte installeras p� n�tverksdisk.
CannotInstallToUNCPath=Installationsprogrammet kan inte installeras p� UNC-s�kv�g.
InvalidPath=Du m�ste ange en fullst�ndig s�kv�g med enhetsbeteckning; till exempel:%n%nC:\Program%n%neller en UNC-s�kv�g i formatet:%n%n\\server\resurs
InvalidDrive=Enheten som du har valt finns inte eller �r inte tillg�nglig. V�lj en annan.
DiskSpaceWarningTitle=Inte tillr�ckligt med diskutrymme
DiskSpaceWarning=Installationsprogrammet beh�ver minst %1 KB ledigt diskutrymme f�r installationen men den valda enheten har bara %2 KB tillg�ngligt.%n%nVill du forts�tta �nd�?
DirNameTooLong=Katalogens namn eller s�kv�g �r f�r l�ng.
InvalidDirName=Katalogens namn �r inte giltigt.
BadDirName32=Katalogens namn f�r inte inneh�lla n�got av f�ljande tecken:%n%n%1
DirExistsTitle=Katalogen finns
DirExists=Katalogen:%n%n%1%n%nfinns redan. Vill du �nd� forts�tta installationen till den valda katalogen?
DirDoesntExistTitle=Katalogen finns inte
DirDoesntExist=Katalogen:%n%n%1%n%nfinns inte. Vill du skapa den?

; *** "Select Components" wizard page
WizardSelectComponents=V�lj komponenter
SelectComponentsDesc=Vilka komponenter skall installeras?
SelectComponentsLabel2=V�lj de komponenter som du vill ska installeras; avmarkera de komponenter som du inte vill ha. Klicka sedan p� N�sta n�r du �r klar att forts�tta.
FullInstallation=Fullst�ndig installation
; if possible don't translate 'Compact' as 'Minimal' (I mean 'Minimal' in your language)
CompactInstallation=Kompakt installation
CustomInstallation=Anpassad installation
NoUninstallWarningTitle=Komponenter finns
NoUninstallWarning=Installationsprogrammet har uppt�ckt att f�ljande komponenter redan finns installerade p� din dator:%n%n%1%n%nAtt  avmarkera dessa komponenter kommer inte att avinstallera dom.%n%nVill du forts�tta �nd�?
ComponentSize1=%1 KB
ComponentSize2=%1 MB
ComponentsDiskSpaceGBLabel=Aktuella val kr�ver minst [gb] GB diskutrymme.
ComponentsDiskSpaceMBLabel=Aktuella val kr�ver minst [mb] MB diskutrymme.

; *** "Select Additional Tasks" wizard page
WizardSelectTasks=V�lj extra uppgifter
SelectTasksDesc=Vilka extra uppgifter skall utf�ras?
SelectTasksLabel2=Markera ytterligare uppgifter att utf�ra vid installation av [name], tryck sedan p� N�sta.

; *** "Select Start Menu Folder" wizard page
WizardSelectProgramGroup=V�lj Startmenykatalogen
SelectStartMenuFolderDesc=Var skall installationsprogrammet placera programmets genv�gar?
SelectStartMenuFolderLabel3=Installationsprogrammet kommer att skapa programmets genv�gar i f�ljande katalog.
SelectStartMenuFolderBrowseLabel=F�r att forts�tta klickar du p� N�sta. Om du vill v�lja en annan katalog, klickar du p� Bl�ddra.
MustEnterGroupName=Du m�ste ange ett katalognamn.
GroupNameTooLong=Katalogens namn eller s�kv�g �r f�r l�ng.
InvalidGroupName=Katalogens namn �r inte giltigt.
BadGroupName=Katalognamnet kan inte inneh�lla n�gon av f�ljande tecken:%n%n%1
NoProgramGroupCheck2=&Skapa ingen Startmenykatalog

; *** "Ready to Install" wizard page
WizardReady=Redo att installera
ReadyLabel1=Installationsprogrammet �r nu redo att installera [name] p� din dator.
ReadyLabel2a=Tryck p� Installera om du vill forts�tta, eller p� g� Tillbaka om du vill granska eller �ndra p� n�got.
ReadyLabel2b=V�lj Installera f�r att p�b�rja installationen.
ReadyMemoUserInfo=Anv�ndarinformation:
ReadyMemoDir=Installationsplats:
ReadyMemoType=Installationstyp:
ReadyMemoComponents=Valda komponenter:
ReadyMemoGroup=Startmenykatalog:
ReadyMemoTasks=Extra uppgifter:

; *** TDownloadWizardPage wizard page and DownloadTemporaryFile
DownloadingLabel=H�mtar ner ytterligare filer...
ButtonStopDownload=&Stoppa h�mtningen
StopDownload=�r du s�ker p� att du vill stoppa h�mtningen?
ErrorDownloadAborted=H�mtningen avbruten
ErrorDownloadFailed=H�mtningen misslyckades: %1 %2
ErrorDownloadSizeFailed=F� storlek misslyckades: %1 %2
ErrorFileHash1=Filhash misslyckades: %1
ErrorFileHash2=Ogiltig filhash: f�rv�ntade %1, fick %2
ErrorProgress=Ogiltigt f�rlopp: %1 av %2
ErrorFileSize=Ogiltig filstorlek: f�rv�ntade %1, fick %2

; *** TExtractionWizardPage wizard page and Extract7ZipArchive
ExtractionLabel=Extraherar ytterligare filer...
ButtonStopExtraction=&Stoppa extrahering
StopExtraction=�r du s�ker p� att du vill stoppa extraheringen?
ErrorExtractionAborted=Extrahering avbr�ts
ErrorExtractionFailed=Extrahering misslyckades: %1

; *** "Preparing to Install" wizard page
WizardPreparing=F�rbereder installationen
PreparingDesc=Installationsprogrammet f�rbereder installationen av [name] p� din dator.
PreviousInstallNotCompleted=Installationen/avinstallationen av ett tidigare program har inte slutf�rts. Du m�ste starta om datorn f�r att avsluta den installationen.%n%nEfter att ha startat om datorn k�r du installationsprogrammet igen f�r att slutf�ra installationen av [name].
CannotContinue=Installationsprogrammet kan inte forts�tta. Klicka p� Avbryt f�r att avsluta.
ApplicationsFound=F�ljande program anv�nder filer som m�ste uppdateras av installationsprogrammet. Vi rekommenderar att du l�ter installationsprogrammet automatiskt st�nga dessa program.
ApplicationsFound2=F�ljande program anv�nder filer som m�ste uppdateras av installationsprogrammet. Vi rekommenderar att du l�ter installationsprogrammet automatiskt st�nga dessa program. Efter installationen kommer Setup att f�rs�ka starta programmen igen.
CloseApplications=S&t�ng programmen automatiskt
DontCloseApplications=&St�ng inte programmen
ErrorCloseApplications=Installationsprogrammet kunde inte st�nga alla program. Innan installationen forts�tter rekommenderar vi att du st�nger alla program som anv�nder filer som installationsprogrammet beh�ver uppdatera.
PrepareToInstallNeedsRestart=Installationen m�ste starta om din dator. N�r du har startat om datorn k�r du installationsprogrammet igen f�r att slutf�ra installationen av [name].%n%nVill du starta om nu?

; *** "Installing" wizard page
WizardInstalling=Installerar
InstallingLabel=V�nta under tiden [name] installeras p� din dator.

; *** "Setup Completed" wizard page
FinishedHeadingLabel=Avslutar installationen av [name]
FinishedLabelNoIcons=[name] har nu installerats p� din dator.
FinishedLabel=[name] har nu installerats p� din dator. Programmet kan startas genom att v�lja n�gon av de installerade ikonerna.
ClickFinish=V�lj Slutf�r f�r att avsluta installationen.
FinishedRestartLabel=F�r att slutf�ra installationen av [name] s� m�ste datorn startas om. Vill du starta om nu?
FinishedRestartMessage=F�r att slutf�ra installationen av [name] s� m�ste datorn startas om.%n%nVill du starta om datorn nu?
ShowReadmeCheck=Ja, jag vill se filen L�SMIG
YesRadio=&Ja, jag vill starta om datorn nu
NoRadio=&Nej, jag startar sj�lv om datorn senare
; used for example as 'Run MyProg.exe'
RunEntryExec=K�r %1
; used for example as 'View Readme.txt'
RunEntryShellExec=Visa %1

; *** "Setup Needs the Next Disk" stuff
ChangeDiskTitle=Installationsprogrammet beh�ver n�sta diskett
SelectDiskLabel2=Mata in diskett %1 och tryck OK.%n%nOm filerna kan hittas i en annan katalog �n den som visas nedan, skriv in r�tt s�kv�g eller v�lj Bl�ddra.
PathLabel=&S�kv�g:
FileNotInDir2=Kunde inte hitta filen "%1" i "%2". Var god s�tt i korrekt diskett eller v�lj en annan katalog.
SelectDirectoryLabel=Ange s�kv�gen f�r n�sta diskett.

; *** Installation phase messages
SetupAborted=Installationen slutf�rdes inte.%n%nR�tta till felet och k�r installationen igen.
AbortRetryIgnoreSelectAction=V�lj �tg�rd
AbortRetryIgnoreRetry=&F�rs�k igen
AbortRetryIgnoreIgnore=&Ignorera felet och forts�tt
AbortRetryIgnoreCancel=Avbryt installationen

; *** Installation status messages
StatusClosingApplications=St�nger programmen...
StatusCreateDirs=Skapar kataloger...
StatusExtractFiles=Packar upp filer...
StatusCreateIcons=Skapar programikoner...
StatusCreateIniEntries=Skriver INI-v�rden...
StatusCreateRegistryEntries=Skriver registerv�rden...
StatusRegisterFiles=Registrerar filer...
StatusSavingUninstall=Sparar information f�r avinstallation...
StatusRunProgram=Slutf�r installationen...
StatusRestartingApplications=Startar om programmen...
StatusRollback=�terst�ller �ndringar...

; *** Misc. errors
ErrorInternal2=Internt fel: %1
ErrorFunctionFailedNoCode=%1 misslyckades
ErrorFunctionFailed=%1 misslyckades; kod %2
ErrorFunctionFailedWithMessage=%1 misslyckades; kod %2.%n%3
ErrorExecutingProgram=Kan inte k�ra filen:%n%1

; *** Registry errors
ErrorRegOpenKey=Fel vid �ppning av registernyckel:%n%1\%2
ErrorRegCreateKey=Kan inte skapa registernyckel:%n%1\%2
ErrorRegWriteKey=Kan inte skriva till registernyckel:%n%1\%2

; *** INI errors
ErrorIniEntry=Kan inte skriva nytt INI-v�rde i filen "%1".

; *** File copying errors
FileAbortRetryIgnoreSkipNotRecommended=&Hoppa �ver den h�r filen (rekommenderas inte)
FileAbortRetryIgnoreIgnoreNotRecommended=&Ignorera felet och forts�tt (rekommenderas inte)
SourceIsCorrupted=K�llfilen �r skadad
SourceDoesntExist=K�llfilen "%1" finns inte
ExistingFileReadOnly2=Den befintliga filen kunde inte bytas ut eftersom den �r markerad som skrivskyddad.
ExistingFileReadOnlyRetry=&Ta bort skrivskyddade attributet och f�rs�k igen
ExistingFileReadOnlyKeepExisting=&Beh�ll den befintliga filen
ErrorReadingExistingDest=Ett fel uppstod vid f�rs�k att l�sa den befintliga filen:
FileExistsSelectAction=V�lj �tg�rd
FileExists2=Filen finns redan.
FileExistsOverwriteExisting=&Skriv �ver den befintliga filen
FileExistsKeepExisting=&Beh�ll befintlig fil
FileExistsOverwriteOrKeepAll=&G�r detta f�r n�sta konflikt
ExistingFileNewerSelectAction=V�lj �tg�rd
ExistingFileNewer2=Den befintliga filen �r nyare �n den som installationsprogrammet f�rs�ker installera.
ExistingFileNewerOverwriteExisting=&Skriv �ver den befintliga filen
ExistingFileNewerKeepExisting=&Beh�ll befintlig fil (rekommenderas)
ExistingFileNewerOverwriteOrKeepAll=&G�r detta f�r n�sta konflikt
ErrorChangingAttr=Ett fel uppstod vid f�rs�k att �ndra attribut p� den befintliga filen:
ErrorCreatingTemp=Ett fel uppstod vid ett f�rs�k att skapa installationskatalogen:
ErrorReadingSource=Ett fel uppstod vid ett f�rs�k att l�sa k�llfilen:
ErrorCopying=Ett fel uppstod vid kopiering av filen:
ErrorReplacingExistingFile=Ett fel uppstod vid ett f�rs�k att ers�tta den befintliga filen:
ErrorRestartReplace=�terstartaErs�tt misslyckades:
ErrorRenamingTemp=Ett fel uppstod vid ett f�rs�k att byta namn p� en fil i installationskatalogen:
ErrorRegisterServer=Kunde inte registrera DLL/OCX: %1
ErrorRegSvr32Failed=RegSvr32 misslyckades med felkod %1
ErrorRegisterTypeLib=Kunde inte registrera typbibliotek: %1

; *** Uninstall display name markings
; used for example as 'My Program (32-bit)'
UninstallDisplayNameMark=%1 (%2)
; used for example as 'My Program (32-bit, All users)'
UninstallDisplayNameMarks=%1 (%2, %3)
UninstallDisplayNameMark32Bit=32-bit
UninstallDisplayNameMark64Bit=64-bit
UninstallDisplayNameMarkAllUsers=Alla anv�ndare
UninstallDisplayNameMarkCurrentUser=Aktuell anv�ndare

; *** Post-installation errors
ErrorOpeningReadme=Ett fel uppstod vid �ppnandet av L�SMIG-filen.
ErrorRestartingComputer=Installationsprogrammet kunde inte starta om datorn. Starta om den manuellt.

; *** Uninstaller messages
UninstallNotFound=Filen "%1" finns inte. Kan inte avinstallera.
UninstallOpenError=Filen "%1" kan inte �ppnas. Kan inte avinstallera
UninstallUnsupportedVer=Avinstallationsloggen "%1" �r i ett format som denna version inte k�nner igen. Kan inte avinstallera
UninstallUnknownEntry=En ok�nd rad (%1) hittades i avinstallationsloggen
ConfirmUninstall=�r du s�ker p� att du vill ta bort %1 och alla tillh�rande komponenter?
UninstallOnlyOnWin64=Denna installation kan endast avinstalleras p� en 64-bitarsversion av Windows.
OnlyAdminCanUninstall=Denna installation kan endast avinstalleras av en anv�ndare med administrativa r�ttigheter.
UninstallStatusLabel=V�nta under tiden %1 tas bort fr�n din dator.
UninstalledAll=%1 �r nu borttaget fr�n din dator.
UninstalledMost=Avinstallationen av %1 �r nu klar.%n%nEn del filer/kataloger gick inte att ta bort. Dessa kan tas bort manuellt.
UninstalledAndNeedsRestart=F�r att slutf�ra avinstallationen av %1 m�ste datorn startas om.%n%nVill du starta om nu?
UninstallDataCorrupted=Filen "%1" �r skadad. Kan inte avinstallera

; *** Uninstallation phase messages
ConfirmDeleteSharedFileTitle=Ta bort delad fil?
ConfirmDeleteSharedFile2=Systemet indikerar att f�ljande delade fil inte l�ngre anv�nds av n�gra program. Vill du ta bort den delade filen?%n%n%1%n%nOm n�got program fortfarande anv�nder denna fil och den raderas, kommer programmet kanske att sluta fungera. Om du �r os�ker, v�lj Nej. Att l�ta filen ligga kvar i systemet kommer inte att orsaka n�gon skada.
SharedFileNameLabel=Filnamn:
SharedFileLocationLabel=Plats:
WizardUninstalling=Avinstallationsstatus
StatusUninstalling=Avinstallerar %1...

; *** Shutdown block reasons
ShutdownBlockReasonInstallingApp=Installerar %1.
ShutdownBlockReasonUninstallingApp=Avinstallerar %1.

; The custom messages below aren't used by Setup itself, but if you make
; use of them in your scripts, you'll want to translate them.

[CustomMessages]
NameAndVersion=%1 version %2
AdditionalIcons=Ytterligare genv�gar:
CreateDesktopIcon=Skapa en &genv�g p� skrivbordet
CreateQuickLaunchIcon=Skapa &en genv�g i Snabbstartf�ltet
ProgramOnTheWeb=%1 p� webben
UninstallProgram=Avinstallera %1
LaunchProgram=Starta %1
AssocFileExtension=Associera %1 med filnamnstill�gget %2
AssocingFileExtension=Associerar %1 med filnamnstill�gget %2...
AutoStartProgramGroupDescription=Autostart:
AutoStartProgram=Starta automatiskt %1
AddonHostProgramNotFound=%1 kunde inte hittas i katalogen du valde.%n%nVill du forts�tta �nd�?
