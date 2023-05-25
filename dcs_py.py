from dcspy.run import run, __version__

try:
    import pyi_splash

    pyi_splash.close()
except ImportError:
    pass

ver = __version__

if __name__ == '__main__':
    run()
