import time

import obsstudio_sdk as obs


def main():
    res = cl.GetSceneList()
    scenes = reversed(tuple(d["sceneName"] for d in res["d"]["responseData"]["scenes"]))

    for sc in scenes:
        print(f"Switching to scene {sc}")
        cl.SetCurrentProgramScene(sc)
        time.sleep(0.5)


if __name__ == "__main__":
    cl = obs.ReqClient()

    main()
