// Reveals text word-by-word for a chatbot-style streaming feel. The backend
// returns the full response in one shot (no token streaming yet), so this
// simulates the reveal client-side once the text arrives — re-triggers
// whenever the `text` prop changes (i.e. a new pipeline run completed).

import { useEffect, useRef, useState } from "react";
import { cn } from "../../lib/utils";

export default function TypewriterText({ text, speed = 22, className, as: Component = "p" }) {
  const [shown, setShown] = useState("");
  const [done, setDone] = useState(false);

  useEffect(() => {
    setShown("");
    setDone(false);
    if (!text) return undefined;

    const words = text.split(" ");
    let i = 0;
    const interval = setInterval(() => {
      i += 1;
      setShown(words.slice(0, i).join(" "));
      if (i >= words.length) {
        clearInterval(interval);
        setDone(true);
      }
    }, speed);

    return () => clearInterval(interval);
  }, [text, speed]);

  return (
    <Component className={cn(className)}>
      {shown}
      {!done && text && <span className="ml-0.5 inline-block h-3.5 w-1.5 animate-pulse bg-brand-400 align-middle" />}
    </Component>
  );
}
