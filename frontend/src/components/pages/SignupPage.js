import React, { useState } from 'react';
import { Alert, Button, Card, Form } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { getErrorMessage } from '../../services/api';

export default function SignupPage() {
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    full_name: '',
    email: '',
    password: '',
    invite_code: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [done, setDone] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await signup(form);
      setDone(true);
      setTimeout(() => navigate('/login'), 1200);
    } catch (err) {
      setError(getErrorMessage(err, 'Signup failed'));
    } finally {
      setSubmitting(false);
    }
  };

  const setField = (key, value) => setForm((prev) => ({ ...prev, [key]: value }));

  return (
    <div className="app-page">
      <section className="app-hero">
        <h1>Create account</h1>
        <p>Registration requires a valid invite code issued by an administrator.</p>
      </section>
      <Card className="app-card">
        <Card.Body>
          <Form onSubmit={onSubmit}>
            <Form.Group className="mb-3">
              <Form.Label>Full name</Form.Label>
              <Form.Control
                className="app-input"
                value={form.full_name}
                onChange={(e) => setField('full_name', e.target.value)}
                required
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Email</Form.Label>
              <Form.Control
                type="email"
                className="app-input"
                value={form.email}
                onChange={(e) => setField('email', e.target.value)}
                required
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Password</Form.Label>
              <Form.Control
                type="password"
                className="app-input"
                minLength={8}
                value={form.password}
                onChange={(e) => setField('password', e.target.value)}
                required
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Invite code</Form.Label>
              <Form.Control
                className="app-input"
                value={form.invite_code}
                onChange={(e) => setField('invite_code', e.target.value)}
                required
              />
            </Form.Group>
            {error && <Alert variant="danger">{error}</Alert>}
            {done && <Alert variant="success">Account created. Redirecting to login...</Alert>}
            <Button type="submit" className="app-button-primary" disabled={submitting}>
              {submitting ? 'Creating account...' : 'Create account'}
            </Button>
          </Form>
          <p className="mt-3 mb-0">
            Already registered? <Link to="/login">Login</Link>
          </p>
        </Card.Body>
      </Card>
    </div>
  );
}
