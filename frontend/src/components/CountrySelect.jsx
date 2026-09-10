import { useState, useRef, useEffect } from "react";

const COUNTRIES = [
  { value: "md", label: "Moldova" },
  { value: "at", label: "Austria" },
  { value: "be", label: "Belgium" },
  { value: "bg", label: "Bulgaria" },
  { value: "hr", label: "Croatia" },
  { value: "cy", label: "Cyprus" },
  { value: "cz", label: "Czech Republic" },
  { value: "dk", label: "Denmark" },
  { value: "ee", label: "Estonia" },
  { value: "fi", label: "Finland" },
  { value: "fr", label: "France" },
  { value: "de", label: "Germany" },
  { value: "gr", label: "Greece" },
  { value: "hu", label: "Hungary" },
  { value: "ie", label: "Ireland" },
  { value: "it", label: "Italy" },
  { value: "lv", label: "Latvia" },
  { value: "lt", label: "Lithuania" },
  { value: "lu", label: "Luxembourg" },
  { value: "mt", label: "Malta" },
  { value: "nl", label: "Netherlands" },
  { value: "pl", label: "Poland" },
  { value: "pt", label: "Portugal" },
  { value: "ro", label: "Romania" },
  { value: "sk", label: "Slovakia" },
  { value: "si", label: "Slovenia" },
  { value: "es", label: "Spain" },
  { value: "se", label: "Sweden" },
];

export default function CountrySelect({ value, onChange, required }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    function handleClick(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const selected = COUNTRIES.find((c) => c.value === value);

  return (
    <div className="country-select" ref={ref}>
      <button
        type="button"
        className="country-select-trigger"
        onClick={() => setOpen((o) => !o)}
      >
        <span style={{ color: selected ? "var(--text)" : "var(--muted)" }}>
          {selected ? selected.label : "Choose one"}
        </span>
        <span className={`country-select-arrow ${open ? "open" : ""}`}>▾</span>
      </button>

      {/* input ascuns, doar ca să meargă `required` cu formularul */}
      <input type="hidden" value={value} required={required} />

      {open && (
        <ul className="country-select-list custom-scroll">
          {COUNTRIES.map((c) => (
            <li
              key={c.value}
              className={`country-select-option ${c.value === value ? "selected" : ""}`}
              onClick={() => {
                onChange(c.value);
                setOpen(false);
              }}
            >
              {c.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}