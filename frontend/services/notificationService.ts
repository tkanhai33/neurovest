export type NotificationRecord = {
  id: string;
  category: string;
  title: string;
  message: string;
  severity: string;
  delivery_status: string;
  delivered_at: string | null;
  is_read: boolean;
  read_at: string | null;
  acknowledged_at: string | null;
  created_at: string | null;
};


export type NotificationListResponse = {
  status?: string;
  owner_scoped?: boolean;
  count?: number;
  unread_count?: number;
  records?: NotificationRecord[];
  detail?: string;
};


export type NotificationAction =
  | "read"
  | "acknowledge";


type NotificationErrorResponse = {
  detail?: string;
};


export async function fetchNotifications(
  options?: {
    limit?: number;
    signal?: AbortSignal;
  },
): Promise<NotificationListResponse> {
  const limit =
    options?.limit ?? 100;

  const response =
    await fetch(
      `/api/v1/notifications?limit=${encodeURIComponent(
        String(limit)
      )}`,
      {
        method: "GET",
        credentials:
          "include",
        cache:
          "no-store",
        headers: {
          Accept:
            "application/json",
        },
        signal:
          options?.signal,
      }
    );

  const body =
    (
      await response.json()
    ) as NotificationListResponse;

  if (!response.ok) {
    const errorBody =
      body as NotificationListResponse
      &
      NotificationErrorResponse;

    throw new Error(
      errorBody.detail
      ||
      `Notification request failed with status ${response.status}.`
    );
  }

  return body;
}


export async function applyNotificationAction(
  notificationId: string,
  action: NotificationAction,
  options?: {
    signal?: AbortSignal;
  },
): Promise<void> {
  const response =
    await fetch(
      `/api/v1/notifications/${encodeURIComponent(
        notificationId
      )}/${action}`,
      {
        method:
          "PATCH",
        credentials:
          "include",
        cache:
          "no-store",
        headers: {
          Accept:
            "application/json",
        },
        signal:
          options?.signal,
      }
    );

  const body =
    (
      await response.json()
    ) as NotificationErrorResponse;

  if (!response.ok) {
    throw new Error(
      body.detail
      ||
      `Notification update failed with status ${response.status}.`
    );
  }
}
