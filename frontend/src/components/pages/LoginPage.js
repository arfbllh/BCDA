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
    <div className="app-page auth-shell">
      <section className="app-hero">
        <h1>Login</h1>
        <p>Sign in to access uploads and authenticated workflows.</p>
      </section>
      <Card className="app-card auth-card">
        <Card.Body>
          <Form onSubmit={onSubmit}>
            <Form.Group className="mb-3">
              <Form.Label>Email</Form.Label>
              <Form.Control
                type="email"
                className="app-input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Password</Form.Label>
              <Form.Control
                type="password"
                className="app-input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </Form.Group>
            {error && <Alert variant="danger">{error}</Alert>}
            <Button type="submit" className="app-button-primary" disabled={submitting}>
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
