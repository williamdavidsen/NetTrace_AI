import Link from "next/link";

import type { Scan } from "@/lib/types";
import { formatDateTime } from "@/lib/format";

export function ScansTable({ scans }: { scans: Scan[] }) {
  return (
    <div className="table-wrap panel">
      <table>
        <thead>
          <tr>
            <th>Target</th>
            <th>Status</th>
            <th>Started</th>
            <th>Finished</th>
          </tr>
        </thead>
        <tbody>
          {scans.map((scan) => (
            <tr key={scan.id}>
              <td>
                <Link href={`/scans/${scan.id}`}>{scan.target_name}</Link>
              </td>
              <td>{scan.status}</td>
              <td>{formatDateTime(scan.started_at)}</td>
              <td>{scan.finished_at ? formatDateTime(scan.finished_at) : "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
