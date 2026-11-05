"use client";

import {
  createElement,
  useEffect,
  useRef,
  useState,
} from "react";



type ModelViewerElement = HTMLElement & {
  loaded?: boolean;
  availableAnimations?: string[];
  animationName?: string;
  play?: () => void;
};



/*
 * Temporary production hold.
 *
 * Keep this false while Neuro uses the permanent static hero image.
 *
 * The GLB integration remains intact below so the animated model can
 * be re-enabled later without rebuilding the integration.
 */
const ENABLE_ANIMATED_NEURO = false;



export default function NeuroHeroModel() {
  const [moduleReady, setModuleReady] = useState(false);
  const [modelLoaded, setModelLoaded] = useState(false);
  const [modelError, setModelError] = useState(false);

  const modelRef =
    useRef<ModelViewerElement | null>(null);

  const modelStageRef =
    useRef<HTMLDivElement | null>(null);



  useEffect(() => {
    if (!ENABLE_ANIMATED_NEURO) {
      return;
    }

    let mounted = true;

    import("@google/model-viewer")
      .then(() => {
        if (mounted) {
          setModuleReady(true);
        }
      })
      .catch(() => {
        if (mounted) {
          setModelError(true);
        }
      });

    return () => {
      mounted = false;
    };
  }, []);



  useEffect(() => {
    if (
      !ENABLE_ANIMATED_NEURO ||
      !moduleReady
    ) {
      return;
    }

    const model =
      modelStageRef.current?.querySelector(
        "model-viewer",
      ) as ModelViewerElement | null;

    modelRef.current = model;

    if (!model) {
      return;
    }



    const handleLoad = () => {
      setModelLoaded(true);
      setModelError(false);

      try {
        const animations =
          model.availableAnimations ?? [];

        if (
          animations.length > 0 &&
          !model.animationName
        ) {
          model.animationName =
            animations[0];
        }

        if (
          typeof model.play ===
          "function"
        ) {
          model.play();
        }
      } catch {
        // Future animation path remains non-fatal.
      }
    };



    const handleError = () => {
      setModelLoaded(false);
      setModelError(true);
    };



    model.addEventListener(
      "load",
      handleLoad,
    );

    model.addEventListener(
      "error",
      handleError,
    );



    if (model.loaded) {
      handleLoad();
    }



    return () => {
      model.removeEventListener(
        "load",
        handleLoad,
      );

      model.removeEventListener(
        "error",
        handleError,
      );
    };
  }, [
    moduleReady,
  ]);



  const animatedVisible =
    ENABLE_ANIMATED_NEURO &&
    moduleReady &&
    modelLoaded &&
    !modelError;



  return (
    <div className="neuroModelRoot">

      <div
        className={
          animatedVisible
            ? "neuroModelFallback neuroModelFallbackHidden"
            : "neuroModelFallback neuroModelFallbackVisible"
        }
      >
        <img
          src="/images/neuro/neuro-hero.png"
          alt="Neuro, NeuroVest's investment intelligence companion"
        />
      </div>



      {ENABLE_ANIMATED_NEURO &&
        moduleReady &&
        !modelError && (
          <div
            ref={modelStageRef}
            className={
              modelLoaded
                ? "neuroModelStage neuroModelStageVisible"
                : "neuroModelStage neuroModelStageLoading"
            }
          >
            {createElement(
              "model-viewer",
              {
                src:
                  "/images/neuro/neuro_walking.glb",

                alt:
                  "Neuro, NeuroVest's animated investment intelligence companion",

                autoplay:
                  true,

                "animation-crossfade-duration":
                  "350",

                "camera-controls":
                  true,

                "disable-pan":
                  true,

                "disable-zoom":
                  true,

                "interaction-prompt":
                  "none",

                "shadow-intensity":
                  "0.55",

                "shadow-softness":
                  "0.9",

                exposure:
                  "1.1",

                "environment-image":
                  "neutral",

                style: {
                  width:
                    "100%",

                  height:
                    "100%",

                  background:
                    "transparent",

                  display:
                    "block",
                },
              },
            )}
          </div>
        )}

    </div>
  );
}
