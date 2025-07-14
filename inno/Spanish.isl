; *** Inno Setup version 6.4.0+ Spanish messages ***
;
; Maintained by Jorge Andres Brugger (jbrugger@ideaworks.com.ar)
; Spanish.isl version 1.6.0 (20241226)
; Default.isl version 6.4.0
;
; Thanks to Germ�n Giraldo, Jordi Latorre, Ximo Tamarit, Emiliano Llano,
; Ram�n Verduzco, Graciela Garc�a,  Carles Millan and Rafael Barranco-Droege

[LangOptions]
; The following three entries are very important. Be sure to read and
; understand the '[LangOptions] section' topic in the help file.
LanguageName=Espa<00F1>ol
LanguageID=$0c0a
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

[Messages]

; *** Application titles
SetupAppTitle=Instalar
SetupWindowTitle=Instalar - %1
UninstallAppTitle=Desinstalar
UninstallAppFullTitle=Desinstalar - %1

; *** Misc. common
InformationTitle=Informaci�n
ConfirmTitle=Confirmar
ErrorTitle=Error

; *** SetupLdr messages
SetupLdrStartupMessage=Este programa instalar� %1. �Desea continuar?
LdrCannotCreateTemp=Imposible crear archivo temporal. Instalaci�n interrumpida
LdrCannotExecTemp=Imposible ejecutar archivo en la carpeta temporal. Instalaci�n interrumpida
HelpTextNote=

; *** Startup error messages
LastErrorMessage=%1.%n%nError %2: %3
SetupFileMissing=El archivo %1 no se encuentra en la carpeta de instalaci�n. Por favor, solucione el problema u obtenga una copia nueva del programa.
SetupFileCorrupt=Los archivos de instalaci�n est�n da�ados. Por favor, obtenga una copia nueva del programa.
SetupFileCorruptOrWrongVer=Los archivos de instalaci�n est�n da�ados o son incompatibles con esta versi�n del programa de instalaci�n. Por favor, solucione el problema u obtenga una copia nueva del programa.
InvalidParameter=Se ha utilizado un par�metro no v�lido en la l�nea de comandos:%n%n%1
SetupAlreadyRunning=El programa de instalaci�n a�n est� ejecut�ndose.
WindowsVersionNotSupported=Este programa no es compatible con la versi�n de Windows de su equipo.
WindowsServicePackRequired=Este programa requiere %1 Service Pack %2 o posterior.
NotOnThisPlatform=Este programa no se ejecutar� en %1.
OnlyOnThisPlatform=Este programa debe ejecutarse en %1.
OnlyOnTheseArchitectures=Este programa solo puede instalarse en versiones de Windows dise�adas para las siguientes arquitecturas de procesadores:%n%n%1
WinVersionTooLowError=Este programa requiere %1 versi�n %2 o posterior.
WinVersionTooHighError=Este programa no puede instalarse en %1 versi�n %2 o posterior.
AdminPrivilegesRequired=Debe iniciar la sesi�n como administrador para instalar este programa.
PowerUserPrivilegesRequired=Debe iniciar la sesi�n como administrador o como miembro del grupo de Usuarios Avanzados para instalar este programa.
SetupAppRunningError=El programa de instalaci�n ha detectado que %1 est� ejecut�ndose.%n%nPor favor, ci�rrelo ahora, luego haga clic en Aceptar para continuar o en Cancelar para salir.
UninstallAppRunningError=El desinstalador ha detectado que %1 est� ejecut�ndose.%n%nPor favor, ci�rrelo ahora, luego haga clic en Aceptar para continuar o en Cancelar para salir.

; *** Startup questions
PrivilegesRequiredOverrideTitle=Selecci�n del Modo de Instalaci�n
PrivilegesRequiredOverrideInstruction=Seleccione el modo de instalaci�n
PrivilegesRequiredOverrideText1=%1 puede ser instalado para todos los usuarios (requiere privilegios administrativos), o solo para Ud.
PrivilegesRequiredOverrideText2=%1 puede ser instalado solo para Ud, o para todos los usuarios (requiere privilegios administrativos).
PrivilegesRequiredOverrideAllUsers=Instalar para &todos los usuarios
PrivilegesRequiredOverrideAllUsersRecommended=Instalar para &todos los usuarios (recomendado)
PrivilegesRequiredOverrideCurrentUser=Instalar para &m� solamente
PrivilegesRequiredOverrideCurrentUserRecommended=Instalar para &m� solamente (recomendado)

; *** Misc. errors
ErrorCreatingDir=El programa de instalaci�n no pudo crear la carpeta "%1"
ErrorTooManyFilesInDir=Imposible crear un archivo en la carpeta "%1" porque contiene demasiados archivos

; *** Setup common messages
ExitSetupTitle=Salir de la Instalaci�n
ExitSetupMessage=La instalaci�n no se ha completado a�n. Si cancela ahora, el programa no se instalar�.%n%nPuede ejecutar nuevamente el programa de instalaci�n en otra ocasi�n para completarla.%n%n�Salir de la instalaci�n?
AboutSetupMenuItem=&Acerca de Instalar...
AboutSetupTitle=Acerca de Instalar
AboutSetupMessage=%1 versi�n %2%n%3%n%n%1 sitio Web:%n%4
AboutSetupNote=
TranslatorNote=Spanish translation maintained by Jorge Andres Brugger (jbrugger@gmx.net)

; *** Buttons
ButtonBack=< &Atr�s
ButtonNext=&Siguiente >
ButtonInstall=&Instalar
ButtonOK=Aceptar
ButtonCancel=Cancelar
ButtonYes=&S�
ButtonYesToAll=S� a &Todo
ButtonNo=&No
ButtonNoToAll=N&o a Todo
ButtonFinish=&Finalizar
ButtonBrowse=&Examinar...
ButtonWizardBrowse=&Examinar...
ButtonNewFolder=&Crear Nueva Carpeta

; *** "Select Language" dialog messages
SelectLanguageTitle=Seleccione el Idioma de la Instalaci�n
SelectLanguageLabel=Seleccione el idioma a utilizar durante la instalaci�n.

; *** Common wizard text
ClickNext=Haga clic en Siguiente para continuar o en Cancelar para salir de la instalaci�n.
BeveledLabel=
BrowseDialogTitle=Buscar Carpeta
BrowseDialogLabel=Seleccione una carpeta y luego haga clic en Aceptar.
NewFolderName=Nueva Carpeta

; *** "Welcome" wizard page
WelcomeLabel1=Bienvenido al asistente de instalaci�n de [name]
WelcomeLabel2=Este programa instalar� [name/ver] en su sistema.%n%nSe recomienda cerrar todas las dem�s aplicaciones antes de continuar.

; *** "License Agreement" wizard page
WizardLicense=Acuerdo de Licencia
LicenseLabel=Es importante que lea la siguiente informaci�n antes de continuar.
LicenseLabel3=Por favor, lea el siguiente acuerdo de licencia. Debe aceptar las cl�usulas de este acuerdo antes de continuar con la instalaci�n.
LicenseAccepted=A&cepto el acuerdo
LicenseNotAccepted=&No acepto el acuerdo

; *** "Information" wizard pages
WizardInfoBefore=Informaci�n
InfoBeforeLabel=Es importante que lea la siguiente informaci�n antes de continuar.
InfoBeforeClickLabel=Cuando est� listo para continuar con la instalaci�n, haga clic en Siguiente.
WizardInfoAfter=Informaci�n
InfoAfterLabel=Es importante que lea la siguiente informaci�n antes de continuar.
InfoAfterClickLabel=Cuando est� listo para continuar, haga clic en Siguiente.

; *** "User Information" wizard page
WizardUserInfo=Informaci�n de Usuario
UserInfoDesc=Por favor, introduzca sus datos.
UserInfoName=Nombre de &Usuario:
UserInfoOrg=&Organizaci�n:
UserInfoSerial=N�mero de &Serie:
UserInfoNameRequired=Debe introducir un nombre.

; *** "Select Destination Location" wizard page
WizardSelectDir=Seleccione la Carpeta de Destino
SelectDirDesc=�D�nde debe instalarse [name]?
SelectDirLabel3=El programa instalar� [name] en la siguiente carpeta.
SelectDirBrowseLabel=Para continuar, haga clic en Siguiente. Si desea seleccionar una carpeta diferente, haga clic en Examinar.
DiskSpaceGBLabel=Se requieren al menos [gb] GB de espacio libre en el disco.
DiskSpaceMBLabel=Se requieren al menos [mb] MB de espacio libre en el disco.
CannotInstallToNetworkDrive=El programa de instalaci�n no puede realizar la instalaci�n en una unidad de red.
CannotInstallToUNCPath=El programa de instalaci�n no puede realizar la instalaci�n en una ruta de acceso UNC.
InvalidPath=Debe introducir una ruta completa con la letra de la unidad; por ejemplo:%n%nC:\APP%n%no una ruta de acceso UNC de la siguiente forma:%n%n\\servidor\compartido
InvalidDrive=La unidad o ruta de acceso UNC que seleccion� no existe o no es accesible. Por favor, seleccione otra.
DiskSpaceWarningTitle=Espacio Insuficiente en Disco
DiskSpaceWarning=La instalaci�n requiere al menos %1 KB de espacio libre, pero la unidad seleccionada solo cuenta con %2 KB disponibles.%n%n�Desea continuar de todas formas?
DirNameTooLong=El nombre de la carpeta o la ruta son demasiado largos.
InvalidDirName=El nombre de la carpeta no es v�lido.
BadDirName32=Los nombres de carpetas no pueden incluir los siguientes caracteres:%n%n%1
DirExistsTitle=La Carpeta Ya Existe
DirExists=La carpeta:%n%n%1%n%nya existe. �Desea realizar la instalaci�n en esa carpeta de todas formas?
DirDoesntExistTitle=La Carpeta No Existe
DirDoesntExist=La carpeta:%n%n%1%n%nno existe. �Desea crear esa carpeta?

; *** "Select Components" wizard page
WizardSelectComponents=Seleccione los Componentes
SelectComponentsDesc=�Qu� componentes deben instalarse?
SelectComponentsLabel2=Seleccione los componentes que desea instalar y desmarque los componentes que no desea instalar. Haga clic en Siguiente cuando est� listo para continuar.
FullInstallation=Instalaci�n Completa
; if possible don't translate 'Compact' as 'Minimal' (I mean 'Minimal' in your language)
CompactInstallation=Instalaci�n Compacta
CustomInstallation=Instalaci�n Personalizada
NoUninstallWarningTitle=Componentes Encontrados
NoUninstallWarning=El programa de instalaci�n ha detectado que los siguientes componentes ya est�n instalados en su sistema:%n%n%1%n%nDesmarcar estos componentes no los desinstalar�.%n%n�Desea continuar de todos modos?
ComponentSize1=%1 KB
ComponentSize2=%1 MB
ComponentsDiskSpaceGBLabel=La selecci�n actual requiere al menos [gb] GB de espacio en disco.
ComponentsDiskSpaceMBLabel=La selecci�n actual requiere al menos [mb] MB de espacio en disco.

; *** "Select Additional Tasks" wizard page
WizardSelectTasks=Seleccione las Tareas Adicionales
SelectTasksDesc=�Qu� tareas adicionales deben realizarse?
SelectTasksLabel2=Seleccione las tareas adicionales que desea que se realicen durante la instalaci�n de [name] y haga clic en Siguiente.

; *** "Select Start Menu Folder" wizard page
WizardSelectProgramGroup=Seleccione la Carpeta del Men� Inicio
SelectStartMenuFolderDesc=�D�nde deben colocarse los accesos directos del programa?
SelectStartMenuFolderLabel3=El programa de instalaci�n crear� los accesos directos del programa en la siguiente carpeta del Men� Inicio.
SelectStartMenuFolderBrowseLabel=Para continuar, haga clic en Siguiente. Si desea seleccionar una carpeta distinta, haga clic en Examinar.
MustEnterGroupName=Debe proporcionar un nombre de carpeta.
GroupNameTooLong=El nombre de la carpeta o la ruta son demasiado largos.
InvalidGroupName=El nombre de la carpeta no es v�lido.
BadGroupName=El nombre de la carpeta no puede incluir ninguno de los siguientes caracteres:%n%n%1
NoProgramGroupCheck2=&No crear una carpeta en el Men� Inicio

; *** "Ready to Install" wizard page
WizardReady=Listo para Instalar
ReadyLabel1=Ahora el programa est� listo para iniciar la instalaci�n de [name] en su sistema.
ReadyLabel2a=Haga clic en Instalar para continuar con el proceso o haga clic en Atr�s si desea revisar o cambiar alguna configuraci�n.
ReadyLabel2b=Haga clic en Instalar para continuar con el proceso.
ReadyMemoUserInfo=Informaci�n del usuario:
ReadyMemoDir=Carpeta de Destino:
ReadyMemoType=Tipo de Instalaci�n:
ReadyMemoComponents=Componentes Seleccionados:
ReadyMemoGroup=Carpeta del Men� Inicio:
ReadyMemoTasks=Tareas Adicionales:

; *** TDownloadWizardPage wizard page and DownloadTemporaryFile
DownloadingLabel=Descargando archivos adicionales...
ButtonStopDownload=&Detener descarga
StopDownload=�Est� seguiro que desea detener la descarga?
ErrorDownloadAborted=Descarga cancelada
ErrorDownloadFailed=Fall� descarga: %1 %2
ErrorDownloadSizeFailed=Fall� obtenci�n de tama�o: %1 %2
ErrorFileHash1=Fall� hash del archivo: %1
ErrorFileHash2=Hash de archivo no v�lido: esperado %1, encontrado %2
ErrorProgress=Progreso no v�lido: %1 de %2
ErrorFileSize=Tama�o de archivo no v�lido: esperado %1, encontrado %2

; *** TExtractionWizardPage wizard page and Extract7ZipArchive
ExtractionLabel=Extrayendo archivos adicionales...
ButtonStopExtraction=&Detener extracci�n
StopExtraction=�Est� seguro que desea detener la extracci�n?
ErrorExtractionAborted=Extracci�n cancelada
ErrorExtractionFailed=Fall� la extracci�n: %1

; *** "Preparing to Install" wizard page
WizardPreparing=Prepar�ndose para Instalar
PreparingDesc=El programa de instalaci�n est� prepar�ndose para instalar [name] en su sistema.
PreviousInstallNotCompleted=La instalaci�n/desinstalaci�n previa de un programa no se complet�. Deber� reiniciar el sistema para completar esa instalaci�n.%n%nUna vez reiniciado el sistema, ejecute el programa de instalaci�n nuevamente para completar la instalaci�n de [name].
CannotContinue=El programa de instalaci�n no puede continuar. Por favor, presione Cancelar para salir.
ApplicationsFound=Las siguientes aplicaciones est�n usando archivos que necesitan ser actualizados por el programa de instalaci�n. Se recomienda que permita al programa de instalaci�n cerrar autom�ticamente estas aplicaciones.
ApplicationsFound2=Las siguientes aplicaciones est�n usando archivos que necesitan ser actualizados por el programa de instalaci�n. Se recomienda que permita al programa de instalaci�n cerrar autom�ticamente estas aplicaciones. Al completarse la instalaci�n, el programa de instalaci�n intentar� reiniciar las aplicaciones.
CloseApplications=&Cerrar autom�ticamente las aplicaciones
DontCloseApplications=&No cerrar las aplicaciones
ErrorCloseApplications=El programa de instalaci�n no pudo cerrar de forma autom�tica todas las aplicaciones. Se recomienda que, antes de continuar, cierre todas las aplicaciones que utilicen archivos que necesitan ser actualizados por el programa de instalaci�n.
PrepareToInstallNeedsRestart=El programa de instalaci�n necesita reiniciar el sistema. Una vez que se haya reiniciado ejecute nuevamente el programa de instalaci�n para completar la instalaci�n de [name].%n%n�Desea reiniciar el sistema ahora?

; *** "Installing" wizard page
WizardInstalling=Instalando
InstallingLabel=Por favor, espere mientras se instala [name] en su sistema.

; *** "Setup Completed" wizard page
FinishedHeadingLabel=Completando la instalaci�n de [name]
FinishedLabelNoIcons=El programa complet� la instalaci�n de [name] en su sistema.
FinishedLabel=El programa complet� la instalaci�n de [name] en su sistema. Puede ejecutar la aplicaci�n utilizando los accesos directos creados.
ClickFinish=Haga clic en Finalizar para salir del programa de instalaci�n.
FinishedRestartLabel=Para completar la instalaci�n de [name], su sistema debe reiniciarse. �Desea reiniciarlo ahora?
FinishedRestartMessage=Para completar la instalaci�n de [name], su sistema debe reiniciarse.%n%n�Desea reiniciarlo ahora?
ShowReadmeCheck=S�, deseo ver el archivo L�AME
YesRadio=&S�, deseo reiniciar el sistema ahora
NoRadio=&No, reiniciar� el sistema m�s tarde
; used for example as 'Run MyProg.exe'
RunEntryExec=Ejecutar %1
; used for example as 'View Readme.txt'
RunEntryShellExec=Ver %1

; *** "Setup Needs the Next Disk" stuff
ChangeDiskTitle=El Programa de Instalaci�n Necesita el Siguiente Disco
SelectDiskLabel2=Por favor, inserte el Disco %1 y haga clic en Aceptar.%n%nSi los archivos pueden ser hallados en una carpeta diferente a la indicada abajo, introduzca la ruta correcta o haga clic en Examinar.
PathLabel=&Ruta:
FileNotInDir2=El archivo "%1" no se ha podido hallar en "%2". Por favor, inserte el disco correcto o seleccione otra carpeta.
SelectDirectoryLabel=Por favor, especifique la ubicaci�n del siguiente disco.

; *** Installation phase messages
SetupAborted=La instalaci�n no se ha completado.%n%nPor favor solucione el problema y ejecute nuevamente el programa de instalaci�n.
AbortRetryIgnoreSelectAction=Seleccione acci�n
AbortRetryIgnoreRetry=&Reintentar
AbortRetryIgnoreIgnore=&Ignorar el error y continuar
AbortRetryIgnoreCancel=Cancelar instalaci�n

; *** Installation status messages
StatusClosingApplications=Cerrando aplicaciones...
StatusCreateDirs=Creando carpetas...
StatusExtractFiles=Extrayendo archivos...
StatusCreateIcons=Creando accesos directos...
StatusCreateIniEntries=Creando entradas INI...
StatusCreateRegistryEntries=Creando entradas de registro...
StatusRegisterFiles=Registrando archivos...
StatusSavingUninstall=Guardando informaci�n para desinstalar...
StatusRunProgram=Terminando la instalaci�n...
StatusRestartingApplications=Reiniciando aplicaciones...
StatusRollback=Deshaciendo cambios...

; *** Misc. errors
ErrorInternal2=Error interno: %1
ErrorFunctionFailedNoCode=%1 fall�
ErrorFunctionFailed=%1 fall�; c�digo %2
ErrorFunctionFailedWithMessage=%1 fall�; c�digo %2.%n%3
ErrorExecutingProgram=Imposible ejecutar el archivo:%n%1

; *** Registry errors
ErrorRegOpenKey=Error al abrir la clave del registro:%n%1\%2
ErrorRegCreateKey=Error al crear la clave del registro:%n%1\%2
ErrorRegWriteKey=Error al escribir la clave del registro:%n%1\%2

; *** INI errors
ErrorIniEntry=Error al crear entrada INI en el archivo "%1".

; *** File copying errors
FileAbortRetryIgnoreSkipNotRecommended=&Omitir este archivo (no recomendado)
FileAbortRetryIgnoreIgnoreNotRecommended=&Ignorar el error y continuar (no recomendado)
SourceIsCorrupted=El archivo de origen est� da�ado
SourceDoesntExist=El archivo de origen "%1" no existe
ExistingFileReadOnly2=El archivo existente no puede ser reemplazado debido a que est� marcado como solo-lectura.
ExistingFileReadOnlyRetry=&Elimine el atributo de solo-lectura y reintente
ExistingFileReadOnlyKeepExisting=&Mantener el archivo existente
ErrorReadingExistingDest=Ocurri� un error mientras se intentaba leer el archivo:
FileExistsSelectAction=Seleccione acci�n
FileExists2=El archivo ya existe.
FileExistsOverwriteExisting=&Sobreescribir el archivo existente
FileExistsKeepExisting=&Mantener el archivo existente
FileExistsOverwriteOrKeepAll=&Hacer lo mismo para los siguientes conflictos
ExistingFileNewerSelectAction=Seleccione acci�n
ExistingFileNewer2=El archivo existente es m�s reciente que el que se est� tratando de instalar.
ExistingFileNewerOverwriteExisting=&Sobreescribir el archivo existente
ExistingFileNewerKeepExisting=&Mantener el archivo existente (recomendado)
ExistingFileNewerOverwriteOrKeepAll=&Hacer lo mismo para lo siguientes conflictos
ErrorChangingAttr=Ocurri� un error al intentar cambiar los atributos del archivo:
ErrorCreatingTemp=Ocurri� un error al intentar crear un archivo en la carpeta de destino:
ErrorReadingSource=Ocurri� un error al intentar leer el archivo de origen:
ErrorCopying=Ocurri� un error al intentar copiar el archivo:
ErrorReplacingExistingFile=Ocurri� un error al intentar reemplazar el archivo existente:
ErrorRestartReplace=Fall� reintento de reemplazar:
ErrorRenamingTemp=Ocurri� un error al intentar renombrar un archivo en la carpeta de destino:
ErrorRegisterServer=Imposible registrar el DLL/OCX: %1
ErrorRegSvr32Failed=RegSvr32 fall� con el c�digo de salida %1
ErrorRegisterTypeLib=Imposible registrar la librer�a de tipos: %1

; *** Uninstall display name markings
; used for example as 'My Program (32-bit)'
UninstallDisplayNameMark=%1 (%2)
; used for example as 'My Program (32-bit, All users)'
UninstallDisplayNameMarks=%1 (%2, %3)
UninstallDisplayNameMark32Bit=32-bit
UninstallDisplayNameMark64Bit=64-bit
UninstallDisplayNameMarkAllUsers=Todos los usuarios
UninstallDisplayNameMarkCurrentUser=Usuario actual

; *** Post-installation errors
ErrorOpeningReadme=Ocurri� un error al intentar abrir el archivo L�AME.
ErrorRestartingComputer=El programa de instalaci�n no pudo reiniciar el equipo. Por favor, h�galo manualmente.

; *** Uninstaller messages
UninstallNotFound=El archivo "%1" no existe. Imposible desinstalar.
UninstallOpenError=El archivo "%1" no pudo ser abierto. Imposible desinstalar
UninstallUnsupportedVer=El archivo de registro para desinstalar "%1" est� en un formato no reconocido por esta versi�n del desinstalador. Imposible desinstalar
UninstallUnknownEntry=Se encontr� una entrada desconocida (%1) en el registro de desinstalaci�n
ConfirmUninstall=�Est� seguro que desea desinstalar completamente %1 y todos sus componentes?
UninstallOnlyOnWin64=Este programa solo puede ser desinstalado en Windows de 64-bits.
OnlyAdminCanUninstall=Este programa solo puede ser desinstalado por un usuario con privilegios administrativos.
UninstallStatusLabel=Por favor, espere mientras %1 es desinstalado de su sistema.
UninstalledAll=%1 se desinstal� satisfactoriamente de su sistema.
UninstalledMost=La desinstalaci�n de %1 ha sido completada.%n%nAlgunos elementos no pudieron eliminarse, pero podr� eliminarlos manualmente si lo desea.
UninstalledAndNeedsRestart=Para completar la desinstalaci�n de %1, su sistema debe reiniciarse.%n%n�Desea reiniciarlo ahora?
UninstallDataCorrupted=El archivo "%1" est� da�ado. No puede desinstalarse

; *** Uninstallation phase messages
ConfirmDeleteSharedFileTitle=�Eliminar Archivo Compartido?
ConfirmDeleteSharedFile2=El sistema indica que el siguiente archivo compartido no es utilizado por ning�n otro programa. �Desea eliminar este archivo compartido?%n%nSi elimina el archivo y hay programas que lo utilizan, esos programas podr�an dejar de funcionar correctamente. Si no est� seguro, elija No. Dejar el archivo en su sistema no producir� ning�n da�o.
SharedFileNameLabel=Archivo:
SharedFileLocationLabel=Ubicaci�n:
WizardUninstalling=Estado de la Desinstalaci�n
StatusUninstalling=Desinstalando %1...

; *** Shutdown block reasons
ShutdownBlockReasonInstallingApp=Instalando %1.
ShutdownBlockReasonUninstallingApp=Desinstalando %1.

; The custom messages below aren't used by Setup itself, but if you make
; use of them in your scripts, you'll want to translate them.

[CustomMessages]

NameAndVersion=%1 versi�n %2
AdditionalIcons=Accesos directos adicionales:
CreateDesktopIcon=Crear un acceso directo en el &escritorio
CreateQuickLaunchIcon=Crear un acceso directo en &Inicio R�pido
ProgramOnTheWeb=%1 en la Web
UninstallProgram=Desinstalar %1
LaunchProgram=Ejecutar %1
AssocFileExtension=&Asociar %1 con la extensi�n de archivo %2
AssocingFileExtension=Asociando %1 con la extensi�n de archivo %2...
AutoStartProgramGroupDescription=Inicio:
AutoStartProgram=Iniciar autom�ticamente %1
AddonHostProgramNotFound=%1 no pudo ser localizado en la carpeta seleccionada.%n%n�Desea continuar de todas formas?
