typedef struct
{
    unsigned int keyIdx         : 8;        // index of the G key or mouse button, for example, 6 for G6 or Button 6
    unsigned int keyDown        : 1;        // key up or down, 1 is down, 0 is up
    unsigned int mState         : 2;        // mState (1, 2 or 3 for M1, M2 and M3)
    unsigned int mouse          : 1;        // indicate if the Event comes from a mouse, 1 is yes, 0 is no.
    unsigned int reserved1      : 4;        // reserved1
    unsigned int reserved2      : 16;       // reserved2
} GkeyCode;

// Callback used to allow client to react to the Gkey events. It is called in the context of another thread.
typedef void (__cdecl *logiGkeyCB)(GkeyCode gkeyCode, const wchar_t* gkeyOrButtonString, void* context);

typedef struct
{
    logiGkeyCB gkeyCallBack;
    void* gkeyContext;
} logiGkeyCBContext;

// Enable the Gkey SDK by calling this function
BOOL LogiGkeyInit(logiGkeyCBContext* gkeyCBContext);

// Check if a mouse button is currently pressed
BOOL LogiGkeyIsMouseButtonPressed(const int buttonNumber);

// Get friendly name for mouse button
wchar_t* LogiGkeyGetMouseButtonString(const int buttonNumber);

// Check if a keyboard G-key is currently pressed
BOOL LogiGkeyIsKeyboardGkeyPressed(const int gkeyNumber,const  int modeNumber);

// Get friendly name for G-key
wchar_t* LogiGkeyGetKeyboardGkeyString(const int gkeyNumber,const  int modeNumber);

// Disable the Gkey SDK, free up all the resources.
void LogiGkeyShutdown();
