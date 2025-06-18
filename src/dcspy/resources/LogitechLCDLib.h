bool LogiLcdInit(wchar_t* friendlyName, int lcdType);
bool LogiLcdIsConnected(int lcdType);
bool LogiLcdIsButtonPressed(int button);
void LogiLcdUpdate();
void LogiLcdShutdown();

// Monochrome LCD functions
bool LogiLcdMonoSetBackground(BYTE monoBitmap[]);
bool LogiLcdMonoSetText(int lineNumber, wchar_t* text);

// Color LCD functions
bool LogiLcdColorSetBackground(BYTE colorBitmap[]);
bool LogiLcdColorSetTitle(wchar_t* text, int red, int green, int blue);
bool LogiLcdColorSetText(int lineNumber, wchar_t* text, int red, int green, int blue);
