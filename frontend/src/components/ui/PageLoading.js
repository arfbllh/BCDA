import React from 'react';
import { Spinner, Stack } from 'react-bootstrap';

/**
 * Centered loading state for full-width page sections.
 */
export default function PageLoading({ message = 'Loading…' }) {
  return (
    <Stack
      direction="horizontal"
      gap={3}
      className="justify-content-center align-items-center py-5 page-loading"
    >
      <Spinner animation="border" role="status" aria-hidden="true" />
      <span className="text-muted">{message}</span>
    </Stack>
  );
}
