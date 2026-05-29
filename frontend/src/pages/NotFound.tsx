import { ArrowLeft, Compass, MessageSquare } from "lucide-react";
import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="mesh-bg grid min-h-dvh place-items-center px-6">
      <div className="animate-rise w-full max-w-md text-center">
        <span className="brand-fill mx-auto grid h-14 w-14 place-items-center rounded-2xl text-white">
          <Compass size={26} strokeWidth={2.2} />
        </span>
        <p className="mt-6 font-display text-6xl font-extrabold leading-none">
          <span className="brand-text">404</span>
        </p>
        <h1 className="mt-4 font-display text-2xl font-bold text-ink">Сторінку не знайдено</h1>
        <p className="mt-3 text-[15px] leading-relaxed text-muted">
          Можливо, посилання застаріло або адресу введено з помилкою.
        </p>
        <div className="mt-8 flex flex-wrap justify-center gap-3">
          <Link to="/support" className="btn btn-gradient">
            <ArrowLeft size={16} strokeWidth={2.3} /> На головну
          </Link>
          <Link to="/documentation" className="btn btn-ghost">
            <MessageSquare size={16} strokeWidth={2.3} /> Документація
          </Link>
        </div>
      </div>
    </div>
  );
}
