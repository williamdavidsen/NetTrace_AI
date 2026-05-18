import { render } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { RealtimeRefresh } from "@/components/realtime-refresh";

const refresh = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ refresh }),
}));

afterEach(() => {
  vi.clearAllMocks();
  vi.useRealTimers();
});

describe("RealtimeRefresh", () => {
  it("refreshes the route on an interval", () => {
    vi.useFakeTimers();

    render(<RealtimeRefresh intervalMs={5000} />);

    expect(refresh).not.toHaveBeenCalled();
    vi.advanceTimersByTime(5000);
    expect(refresh).toHaveBeenCalledTimes(1);
    vi.advanceTimersByTime(5000);
    expect(refresh).toHaveBeenCalledTimes(2);
  });

  it("cleans up polling when unmounted", () => {
    vi.useFakeTimers();
    const { unmount } = render(<RealtimeRefresh intervalMs={5000} />);

    unmount();
    vi.advanceTimersByTime(10000);

    expect(refresh).not.toHaveBeenCalled();
  });
});
