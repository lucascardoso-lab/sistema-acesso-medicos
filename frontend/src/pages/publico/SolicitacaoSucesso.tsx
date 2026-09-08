import { Link, useLocation } from "react-router-dom";

export function SolicitacaoSucesso() {
  const location = useLocation();
  const protocolo = (location.state as { protocolo?: string } | null)?.protocolo;

  return (
    <div className="form-container">
      <h1>Solicitação enviada com sucesso.</h1>
      {protocolo && (
        <p>
          Seu número de protocolo é <strong>{protocolo}</strong>. Guarde-o para acompanhamento.
        </p>
      )}
      <Link to="/solicitacao">Enviar nova solicitação</Link>
    </div>
  );
}
