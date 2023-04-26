from dcspy.run import run
try:
    import pyi_splash
    pyi_splash.close()
except ImportError:
    pass


if __name__ == '__main__':
    run()
