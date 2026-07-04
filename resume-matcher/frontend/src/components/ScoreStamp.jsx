export default function ScoreStamp({ score }) {
  let tier = "low";
  let label = "Weak fit";
  if (score >= 70) {
    tier = "high";
    label = "Strong fit";
  } else if (score >= 40) {
    tier = "mid";
    label = "Partial fit";
  }

  return (
    <div className="stamp-wrap">
      <div className={`stamp ${tier}`}>
        <span className="num">{Math.round(score)}</span>
        <span className="label">/ 100</span>
      </div>
      <div className="stamp-caption">
        <h2>{label}</h2>
        <p>Based on semantic overlap between the resume and each job requirement.</p>
      </div>
    </div>
  );
}
