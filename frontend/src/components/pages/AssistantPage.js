import React, { useMemo, useState } from 'react';
import { Alert, Button, Card, Form } from 'react-bootstrap';

export default function AssistantPage() {
  const [provider, setProvider] = useState('openai');
  const [apiKey, setApiKey] = useState('');
  const [model, setModel] = useState('gpt-4o-mini');
  const [contextText, setContextText] = useState('');
  const [prompt, setPrompt] = useState('Explain this study summary in plain language.');
  const [response, setResponse] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const endpoint = useMemo(() => {
    if (provider === 'openai') return 'https://api.openai.com/v1/chat/completions';
    return '';
  }, [provider]);

  const runPrompt = async (e) => {
    e.preventDefault();
    setError('');
    setResponse('');
    if (!endpoint || !apiKey.trim()) {
      setError('Provide provider and API key. Keys stay in your browser session only.');
      return;
    }
    setLoading(true);
    try {
      const body = {
        model,
        messages: [
          { role: 'system', content: 'You are a concise genomics assistant.' },
          { role: 'user', content: `Context:\n${contextText}\n\nTask:\n${prompt}` },
        ],
      };
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${apiKey.trim()}`,
        },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.error?.message || 'Provider request failed');
      const text = data?.choices?.[0]?.message?.content || '';
      setResponse(text);
    } catch (err) {
      setError(err.message || 'LLM request failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-page">
      <section className="app-hero">
        <h1>AI Assistant</h1>
        <p>Frontend-only assistant for summarizing study outputs and notes.</p>
      </section>
      <Alert variant="warning">
        This assistant runs in your browser and sends selected text to your configured LLM
        provider. Review context before sending sensitive data.
      </Alert>
      <Card className="app-card">
        <Card.Body>
          <Form onSubmit={runPrompt}>
            <Form.Group className="mb-3">
              <Form.Label>Provider</Form.Label>
              <Form.Select className="app-select" value={provider} onChange={(e) => setProvider(e.target.value)}>
                <option value="openai">OpenAI-compatible</option>
              </Form.Select>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>API key (browser only)</Form.Label>
              <Form.Control
                type="password"
                className="app-input"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="sk-..."
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Model</Form.Label>
              <Form.Control className="app-input" value={model} onChange={(e) => setModel(e.target.value)} />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Context</Form.Label>
              <Form.Control
                as="textarea"
                className="app-textarea"
                rows={5}
                value={contextText}
                onChange={(e) => setContextText(e.target.value)}
                placeholder="Paste summary/status/results you want the assistant to analyze."
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Prompt</Form.Label>
              <Form.Control
                as="textarea"
                className="app-textarea"
                rows={3}
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
              />
            </Form.Group>
            {error && <Alert variant="danger">{error}</Alert>}
            <Button type="submit" className="app-button-primary" disabled={loading}>
              {loading ? 'Thinking...' : 'Run assistant'}
            </Button>
          </Form>
          {response && (
            <div className="app-section-card mt-3">
              <h2 className="app-section-heading">Assistant output</h2>
              <pre className="jobs-result-pre mt-0 mb-0">{response}</pre>
            </div>
          )}
        </Card.Body>
      </Card>
    </div>
  );
}
