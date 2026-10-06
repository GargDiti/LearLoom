import { useEffect, useState } from "react";
import confused from "../assets/moods/confused.png";
import sleepy from "../assets/moods/sleepy.png";
import crying from "../assets/moods/crying.png";
import happy from "../assets/moods/happy.png";
import "./LoadingLizard.css";

// Each stage pairs a mood sprite with the message shown while it's "thinking"
const STAGES = [
  { img: confused, text: "Reading the page..." },
  { img: sleepy, text: "Digging through sources..." },
  { img: crying, text: "Untangling the details..." },
  { img: happy, text: "Wrapping up your summary..." },
];

function LoadingLizard({ onDone }) {
  const [stageIndex, setStageIndex] = useState(0);

  useEffect(() => {
    if (stageIndex >= STAGES.length - 1) {
      const finishTimer = setTimeout(() => {
        onDone?.();
      }, 900);
      return () => clearTimeout(finishTimer);
    }

    const timer = setTimeout(() => {
      setStageIndex((i) => i + 1);
    }, 850);

    return () => clearTimeout(timer);
  }, [stageIndex, onDone]);

  const stage = STAGES[stageIndex];

  return (
    <div className="loading-lizard">
      <div className="loading-lizard-sprite-wrap">
        <img
          key={stageIndex}
          src={stage.img}
          alt="Reading Lizard thinking"
          className="loading-lizard-sprite"
        />
        <span className="loading-lizard-zzz">✦</span>
      </div>

      <p className="loading-lizard-text">{stage.text}</p>

      <div className="loading-lizard-dots">
        {STAGES.map((_, i) => (
          <span
            key={i}
            className={
              "loading-lizard-dot" + (i <= stageIndex ? " is-active" : "")
            }
          />
        ))}
      </div>
    </div>
  );
}

export default LoadingLizard;
