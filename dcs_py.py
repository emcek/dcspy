from dcspy.run import __version__, run

try:
    import pyi_splash

    pyi_splash.close()
except ImportError:
    pass

ver = __version__

if __name__ == '__main__':
    run()
