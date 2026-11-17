import { useEffect, useRef, useState, type FormEvent } from 'react';
import { Bot, Minus, Send, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { ApiError } from '../api/client';
import { sendAssistantMessage } from '../api/assistant';
import type {
  AssistantAvailabilityData,
  AssistantMessageResponse,
  AssistantOrganizationsData,
  AssistantPendingConfirmation,
  AssistantToolResult,
  AssistantVenueOption,
} from '../api/types';
import { useAuth } from '../auth/AuthProvider';

type Message = { from: 'assistant' | 'user'; text: string; results?: AssistantToolResult[] };
type PendingConfirmation = { conversationId: string; confirmationId: string };

function getPendingConfirmation(response: AssistantMessageResponse): PendingConfirmation | null {
  if (!response.pending_confirmation) return null;
  const pending: AssistantPendingConfirmation | undefined = response.state.pending_confirmation;
  if (!pending) return null;
  const confirmationId = pending.confirmation_id;
  return typeof confirmationId === 'string'
    ? { conversationId: response.conversation_id, confirmationId }
    : null;
}

function responseText(response: AssistantMessageResponse) {
  const failures = response.tool_results
    .filter((result) => result.status === 'failed' && result.error)
    .map((result) => result.error)
    .join(' ');
  return failures ? `${response.response} ${failures}` : response.response;
}

function isAvailabilityData(data: unknown): data is AssistantAvailabilityData {
  return typeof data === 'object' && data !== null && Array.isArray((data as AssistantAvailabilityData).available_venues);
}

function isOrganizationsData(data: unknown): data is AssistantOrganizationsData {
  return typeof data === 'object' && data !== null && Array.isArray((data as AssistantOrganizationsData).organizations);
}

function AssistantResults({ results, onVenueSelect, onOrganizationSelect, disabled }: {
  results: AssistantToolResult[];
  onVenueSelect: (venue: AssistantVenueOption) => void;
  onOrganizationSelect: (organization: { id: string; name: string }) => void;
  disabled: boolean;
}) {
  return <>
    {results.map((result, index) => {
      if (result.status !== 'succeeded') return null;
      if (result.name === 'check_availability' && isAvailabilityData(result.data)) {
        const data = result.data;
        return <div className="chat-result" key={`availability-${index}`}>
          {data.messages?.map((message) => <p className="chat-result__notice" key={message}>{message}</p>)}
          {data.available_venues.map((venue) => <article className="chat-result__card" key={venue.id}>
            <strong>{venue.name}</strong><span>{venue.location} · up to {venue.capacity} people</span>
            {venue.description && <small>{venue.description}</small>}
            <button type="button" className="button button--soft button--small" disabled={disabled || !data.booking_ready} onClick={() => onVenueSelect(venue)}>Choose this venue</button>
          </article>)}
          {!data.available_venues.length && !data.messages?.length && <p className="chat-result__notice">No bookable venues match that request. Try another time, capacity, or location.</p>}
        </div>;
      }
      if (result.name === 'list_my_organizations' && isOrganizationsData(result.data)) {
        return <div className="chat-result" key={`organizations-${index}`}>
          {result.data.organizations.map((organization) => <article className="chat-result__card" key={organization.id}>
            <strong>{organization.name}</strong>
            <button type="button" className="button button--soft button--small" disabled={disabled} onClick={() => onOrganizationSelect(organization)}>Book for this organization</button>
          </article>)}
          {!result.data.organizations.length && <p className="chat-result__notice">You do not have an active organizer organization. Ask an administrator to add your organizer membership.</p>}
        </div>;
      }
      return null;
    })}
  </>;
}

export function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    { from: 'assistant', text: "Hi! I'm the UniSpot Assistant. Ask me about the site, events, venues, services, bookings, or your dashboard." },
  ]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [pendingConfirmation, setPendingConfirmation] = useState<PendingConfirmation | null>(null);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState('');
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const launcherRef = useRef<HTMLButtonElement>(null);
  const messageInputRef = useRef<HTMLInputElement>(null);
  const restoreLauncherFocus = useRef(false);

  useEffect(() => {
    if (open) messageInputRef.current?.focus();
    else if (restoreLauncherFocus.current) {
      launcherRef.current?.focus();
      restoreLauncherFocus.current = false;
    }
  }, [open]);

  const closeChat = () => {
    restoreLauncherFocus.current = true;
    setOpen(false);
  };

  const appendResponse = (response: AssistantMessageResponse) => {
    setConversationId(response.conversation_id);
    setMessages((current) => [...current, { from: 'assistant', text: responseText(response), results: response.tool_results }]);
    setPendingConfirmation(getPendingConfirmation(response));
    if (response.tool_results.some((result) => result.status === 'succeeded' && (result.name === 'create_booking' || result.name === 'cancel_my_booking'))) {
      window.dispatchEvent(new Event('unispot:bookings-changed'));
      window.dispatchEvent(new Event('unispot:notifications-changed'));
    }
  };

  const sendAssistantText = async (text: string) => {
    if (!text || isSending) return;
    setError('');
    setMessages((current) => [...current, { from: 'user', text }]);
    setIsSending(true);
    try {
      appendResponse(await sendAssistantMessage({ message: text, conversation_id: conversationId || undefined }));
    } catch (requestError) {
      setError(requestError instanceof ApiError ? requestError.message : 'The assistant is temporarily unavailable.');
    } finally {
      setIsSending(false);
    }
  };

  const sendMessage = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const text = draft.trim();
    if (!text || isSending) return;
    if (!isAuthenticated) {
      setMessages((current) => [...current, { from: 'assistant', text: 'Please log in before using assistant booking.' }]);
      navigate('/login');
      return;
    }
    setDraft('');
    await sendAssistantText(text);
  };

  const chooseVenue = (venue: AssistantVenueOption) => {
    void sendAssistantText(`Use venue ${venue.id} (${venue.name}) for my booking.`);
  };

  const chooseOrganization = (organization: { id: string; name: string }) => {
    void sendAssistantText(`Use organization ${organization.id} (${organization.name}) for my booking.`);
  };

  const confirmPendingAction = async () => {
    if (!pendingConfirmation || isSending) return;
    setError('');
    setIsSending(true);
    try {
      appendResponse(await sendAssistantMessage({
        conversation_id: pendingConfirmation.conversationId,
        message: 'Confirm',
        confirmed: true,
        confirmation_id: pendingConfirmation.confirmationId,
      }));
    } catch (requestError) {
      if (requestError instanceof ApiError && (requestError.status === 404 || requestError.status === 409)) {
        setPendingConfirmation(null);
      }
      setError(requestError instanceof ApiError ? requestError.message : 'The assistant confirmation failed.');
    } finally {
      setIsSending(false);
    }
  };

  const changePendingAction = () => {
    setPendingConfirmation(null);
    setMessages((current) => [...current, { from: 'assistant', text: 'Okay. Tell me what you would like to change.' }]);
  };

  return (
    <>
      {!open && <button ref={launcherRef} className="chat-launcher" type="button" aria-label="Open UniSpot Assistant" onClick={() => setOpen(true)}><Bot size={23} /><span>Ask UniSpot</span></button>}
      {open && (
        <section className="chat-panel" role="region" aria-labelledby="assistant-title">
          <header className="chat-header"><span className="chat-avatar"><Bot size={20} /></span><div><strong id="assistant-title">UniSpot Assistant</strong><small>Ask about the site, events, venues, or bookings</small></div><button className="chat-window-action" type="button" aria-label="Minimize chat" onClick={closeChat}><Minus size={17} /></button><button className="chat-window-action" type="button" aria-label="Close chat" onClick={closeChat}><X size={17} /></button></header>
          <div className="chat-messages" aria-live="polite" aria-relevant="additions">
            {messages.map((message, index) => <div className={`chat-message chat-message--${message.from}`} key={`${message.from}-${index}`}><span>{message.text}</span>{message.from === 'assistant' && message.results && <AssistantResults results={message.results} onVenueSelect={chooseVenue} onOrganizationSelect={chooseOrganization} disabled={isSending} />}</div>)}
            {pendingConfirmation && <div className="chat-quick-actions"><button type="button" className="button button--primary button--small" onClick={() => void confirmPendingAction()} disabled={isSending}>{isSending ? 'Confirming…' : 'Confirm action'}</button><button type="button" className="button button--soft button--small" onClick={changePendingAction} disabled={isSending}>Change request</button></div>}
            {isSending && <p className="form-status">Assistant is thinking…</p>}
            {error && <p className="form-error" role="alert">{error}</p>}
          </div>
          <form className="chat-compose" onSubmit={sendMessage}><label className="sr-only" htmlFor="chat-message">Type a message</label><input ref={messageInputRef} id="chat-message" value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="Ask about the site, events, venues, or bookings…" disabled={isSending} /><button className="chat-send" type="submit" aria-label="Send message" disabled={isSending}><Send size={17} /></button></form>
        </section>
      )}
    </>
  );
}
