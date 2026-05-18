import type { PacketEvent } from "@/lib/types";
import { formatDateTime } from "@/lib/format";

export function EventsTable({ events }: { events: PacketEvent[] }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>Source</th>
            <th>Destination</th>
            <th>Protocol</th>
            <th>Size</th>
          </tr>
        </thead>
        <tbody>
          {events.map((event) => (
            <tr key={event.id}>
              <td>{formatDateTime(event.timestamp)}</td>
              <td>{event.source_ip}:{event.source_port ?? "-"}</td>
              <td>{event.destination_ip}:{event.destination_port ?? "-"}</td>
              <td>{event.protocol}</td>
              <td>{event.packet_size}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
