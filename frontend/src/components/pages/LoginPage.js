import React, { useState } from 'react';
import { Alert, Button, Card, Form } from 'react-bootstrap';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { getErrorMessage } from '../../services/api';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const from = location.state?.from || '/';

  const onSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(getErrorMessage(err, 'Login failed'));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="app-static-page">
      <Card>
        <Card.Body>
          <h1 className="h3 mb-3">Login</h1>
          <p className="text-muted">Sign in to access uploads and advanced features.</p>
          <Form onSubmit={onSubmit}>
            <Form.Group className="mb-3">
              <Form.Label>Email</Form.Label>
              <Form.Control
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Password</Form.Label>
              <Form.Control
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </Form.Group>
            {error && <Alert variant="danger">{error}</Alert>}
            <Button type="submit" disabled={submitting}>
              {submitting ? 'Signing in...' : 'Sign in'}
            </Button>
          </Form>
          <p className="mt-3 mb-0">
            Need an account? <Link to="/signup">Sign up with invite code</Link>
          </p>
        </Card.Body>
      </Card>
    </div>
  );
}
