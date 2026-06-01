export function formatToIST(dateString) {
  if (!dateString) return "N/A";

  try {
    // ✅ FORCE UTC INTERPRETATION
    const utcDate = new Date(
      dateString.includes("Z") ? dateString : dateString + "Z"
    );

    return utcDate.toLocaleString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: true
    });

  } catch {
    return dateString;
  }
}