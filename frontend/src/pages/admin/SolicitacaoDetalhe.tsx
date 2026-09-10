import { useCallback, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
  adicionarObservacao,
  aprovar,
  enviarEmail,
  iniciarAnalise,
  marcarRespondida,
  obterHistorico,
  obterSolicitacao,
  rejeitar,
  urlDocumento,
} from "../../services/solicitacaoAdminApi";
import { STATUS_LABELS, type HistoricoItem, type SolicitacaoDetail } from "../../types/solicitacaoAdmin";

export function SolicitacaoDetalhe() {
  const { id } = useParams<{ id: string }>();
  const solicitacaoId = Number(id);

  const [solicitacao, setSolicitacao] = useState<SolicitacaoDetail | null>(null);
  const [historico, setHistorico] = useState<HistoricoItem[]>([]);
  const [observacao, setObservacao] = useState("");
  const [mensagemEmail, setMensagemEmail] = useState("");
  const [anexoEmail, setAnexoEmail] = useState<File | undefined>(undefined);
  const [anexoInputKey, setAnexoInputKey] = useState(0);
  const [motivoRejeicao, setMotivoRejeicao] = useState("");
  const [mostrarRejeicao, setMostrarRejeicao] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [processando, setProcessando] = useState(false);

  const carregar = useCallback(async () => {
    const [detalhe, eventos] = await Promise.all([
      obterSolicitacao(solicitacaoId),
      obterHistorico(solicitacaoId),
    ]);
    setSolicitacao(detalhe);
    setObservacao(detalhe.observacao_interna ?? "");
    setHistorico(eventos);
  }, [solicitacaoId]);

  useEffect(() => {
    carregar().catch(() => setErro("Não foi possível carregar a solicitação."));
  }, [carregar]);

  async function executar(acao: () => Promise<SolicitacaoDetail>): Promise<boolean> {
    setErro(null);
    setProcessando(true);
    try {
      await acao();
      await carregar();
      setMostrarRejeicao(false);
      setMotivoRejeicao("");
      return true;
    } catch (err) {
      const mensagem =
        (err as { response?: { data?: { detail?: string } } }).response?.data?.detail ??
        "Não foi possível executar a ação.";
      setErro(mensagem);
      return false;
    } finally {
      setProcessando(false);
    }
  }

  if (erro && !solicitacao) return <p className="form-error">{erro}</p>;
  if (!solicitacao) return <p>Carregando...</p>;

  return (
    <div>
      <h1>Solicitação {solicitacao.protocolo}</h1>
      <p>
        Status:{" "}
        <span className={`badge badge-${solicitacao.status}`}>
          {STATUS_LABELS[solicitacao.status]}
        </span>
      </p>

      <div className="card-row">
        <div className="card" style={{ flex: 1 }}>
          <h3>Dados pessoais</h3>
          <p><strong>Nome:</strong> {solicitacao.nome_completo}</p>
          <p><strong>E-mail:</strong> {solicitacao.email}</p>
          <p><strong>Telefone:</strong> {solicitacao.telefone}</p>
        </div>
        <div className="card" style={{ flex: 1 }}>
          <h3>Dados profissionais</h3>
          <p><strong>Conselho:</strong> {solicitacao.conselho}</p>
          <p><strong>UF:</strong> {solicitacao.uf_conselho}</p>
          <p><strong>Número do conselho:</strong> {solicitacao.numero_conselho}</p>
          <p><strong>Especialidade:</strong> {solicitacao.especialidade}</p>
        </div>
      </div>

      <div className="card">
        <h3>Documentos</h3>
        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
          <a href={urlDocumento(solicitacao.id, "documento")} target="_blank" rel="noreferrer">
            Ver documento de identificação
          </a>
          <a href={urlDocumento(solicitacao.id, "foto")} target="_blank" rel="noreferrer">
            Ver foto segurando o documento
          </a>
        </div>
      </div>

      {solicitacao.motivo_rejeicao && (
        <div className="card">
          <h3>Motivo da rejeição</h3>
          <p>{solicitacao.motivo_rejeicao}</p>
        </div>
      )}

      {erro && <p className="form-error">{erro}</p>}

      <div className="acoes">
        {solicitacao.status === "pendente" && (
          <button disabled={processando} onClick={() => executar(() => iniciarAnalise(solicitacao.id))}>
            Iniciar análise
          </button>
        )}
        {solicitacao.status === "em_analise" && (
          <>
            <button disabled={processando} onClick={() => executar(() => aprovar(solicitacao.id))}>
              Aprovar
            </button>
            <button
              className="perigo"
              disabled={processando}
              onClick={() => setMostrarRejeicao(true)}
            >
              Rejeitar
            </button>
          </>
        )}
        {(solicitacao.status === "aprovada" || solicitacao.status === "rejeitada") && (
          <button disabled={processando} onClick={() => executar(() => marcarRespondida(solicitacao.id))}>
            Marcar como respondida
          </button>
        )}
      </div>

      {mostrarRejeicao && (
        <div className="card">
          <h3>Motivo da rejeição</h3>
          <textarea
            rows={3}
            style={{ width: "100%" }}
            value={motivoRejeicao}
            onChange={(e) => setMotivoRejeicao(e.target.value)}
          />
          <div className="acoes">
            <button
              className="perigo"
              disabled={processando || motivoRejeicao.trim().length < 3}
              onClick={() => executar(() => rejeitar(solicitacao.id, motivoRejeicao))}
            >
              Confirmar rejeição
            </button>
            <button className="secundario" onClick={() => setMostrarRejeicao(false)}>
              Cancelar
            </button>
          </div>
        </div>
      )}

      {(solicitacao.status === "aprovada" || solicitacao.status === "rejeitada") && (
        <div className="card">
          <h3>Enviar resposta por e-mail</h3>
          <textarea
            rows={4}
            style={{ width: "100%" }}
            placeholder="Mensagem / dados de acesso a enviar ao médico"
            value={mensagemEmail}
            onChange={(e) => setMensagemEmail(e.target.value)}
          />
          <div className="form-field">
            <label htmlFor="anexo_email">Anexo (opcional — PDF, JPG ou PNG)</label>
            <input
              key={anexoInputKey}
              id="anexo_email"
              type="file"
              accept=".pdf,.jpg,.jpeg,.png"
              onChange={(e) => setAnexoEmail(e.target.files?.[0])}
            />
          </div>
          <div className="acoes">
            <button
              disabled={processando || mensagemEmail.trim().length < 3}
              onClick={async () => {
                const sucesso = await executar(() =>
                  enviarEmail(solicitacao.id, mensagemEmail, anexoEmail)
                );
                if (sucesso) {
                  setMensagemEmail("");
                  setAnexoEmail(undefined);
                  setAnexoInputKey((k) => k + 1);
                }
              }}
            >
              Enviar e-mail
            </button>
          </div>
        </div>
      )}

      <div className="card">
        <h3>Observações internas</h3>
        <textarea
          rows={3}
          style={{ width: "100%" }}
          value={observacao}
          onChange={(e) => setObservacao(e.target.value)}
        />
        <div className="acoes">
          <button
            disabled={processando}
            onClick={() => executar(() => adicionarObservacao(solicitacao.id, observacao))}
          >
            Salvar observação
          </button>
        </div>
      </div>

      <div className="card">
        <h3>Histórico</h3>
        <table>
          <thead>
            <tr>
              <th>Data</th>
              <th>Ação</th>
              <th>Status</th>
              <th>Usuário</th>
              <th>Observação</th>
            </tr>
          </thead>
          <tbody>
            {historico.map((h) => (
              <tr key={h.id}>
                <td>{new Date(h.created_at).toLocaleString("pt-BR")}</td>
                <td>{h.acao}</td>
                <td>
                  {h.status_anterior ?? "-"} → {h.status_novo ?? "-"}
                </td>
                <td>{h.usuario_nome ?? "-"}</td>
                <td>{h.descricao ?? "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
