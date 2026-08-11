import React from 'react';

export const TyreBadge = ({ compound = 'MEDIUM', age = 0 }) => {
  const cmp = String(compound).toUpperCase();
  let colorClass = 'tyre-medium';

  if (cmp.includes('SOFT')) colorClass = 'tyre-soft';
  else if (cmp.includes('HARD')) colorClass = 'tyre-hard';
  else if (cmp.includes('INTER')) colorClass = 'tyre-inter';
  else if (cmp.includes('WET')) colorClass = 'tyre-wet';

  return (
    <span className={`tyre-badge ${colorClass}`}>
      <span>{cmp[0]}</span>
      {age > 0 && <span className="opacity-85 font-normal text-[0.7rem]">L{age}</span>}
    </span>
  );
};
