import React from 'react';

export const GlassCard = ({ children, className = '', title, headerAction }) => {
  return (
    <div className={`glass-panel p-4 ${className}`}>
      {title && (
        <div className="flex items-center justify-between mb-3 border-b border-white/10 pb-2">
          <h3 className="text-sm font-semibold tracking-wider uppercase text-slate-300 font-mono">
            {title}
          </h3>
          {headerAction && <div>{headerAction}</div>}
        </div>
      )}
      {children}
    </div>
  );
};
