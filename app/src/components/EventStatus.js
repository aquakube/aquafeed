
export default function EventStatus({ event, level }) {

  const className = `eventstatus ${level}`;

  return (
    <div className={className}>
      {event}
    </div>
  )
}