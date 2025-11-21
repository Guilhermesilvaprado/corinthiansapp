function Logo() {
  return (
    <div className="flex items-center justify-center space-x-2">
      {/* Ícone - documento com gráfico */}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="w-10 h-10 text-indigo-600"
        viewBox="0 0 24 24"
        fill="currentColor"
      >
        {/* Documento */}
        <path d="M6 2a2 2 0 00-2 2v16l4-2 4 2 4-2 4 2V4a2 2 0 00-2-2H6z" />
        {/* Barras do gráfico */}
        <rect x="8" y="14" width="2" height="4" fill="white" />
        <rect x="11" y="12" width="2" height="6" fill="white" />
        <rect x="14" y="10" width="2" height="8" fill="white" />
      </svg>

      {/* Texto da logo */}
      <span className="text-2xl font-extrabold text-indigo-600 tracking-tight">
        App Fiscal
      </span>
    </div>
  );
}

export default Logo;