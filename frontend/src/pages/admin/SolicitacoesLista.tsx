import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listarSolicitacoes } from "../../services/solicitacaoAdminApi";
import { STATUS_LABELS, type SolicitacaoFiltros, type SolicitacaoListResponse } from "../../types/solicitacaoAdmin";

const FILTROS_INICIAIS: SolicitacaoFiltros = { page: 1, page_size: 20 };

export function SolicitacoesLista() {
  const [filtros, setFiltros] = useState<SolicitacaoFiltros>(FILTROS_INICIAIS);
  const [dados, setDados] = useState<SolicitacaoListResponse | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    listarSolicitacoes(filtros)
      .then(setDados)
      .catch(() => setErro("Não foi possível carregar as solicitações."));
  }, [filtros]);

  function atualizarFiltro<K extends keyof SolicitacaoFiltros>(chave: K, valor: SolicitacaoFiltros[K]) {
    setFiltros((atual) => ({ ...atual, [chave]: valor, page: 1 }));
  }

  const totalPaginas = dados ? Math.max(1, Math.ceil(dados.total / dados.page_size)) : 1;

  return (
    <div>
      <h1>Solicitações</h1>

      <div className="filtros">
        <input
          placeholder="Buscar (nome, e-mail, protocolo)"
          value={filtros.busca ?? ""}
          onChange={(e) => atualizarFiltro("busca", e.target.value)}
        />
        <select
          value={filtros.status ?? ""}
          onChange={(e) => atualizarFiltro("status", e.target.value as SolicitacaoFiltros["status"])}
        >
          <option value="">Todos os status</option>
          {Object.entries(STATUS_LABELS).map(([valor, label]) => (
            <option key={valor} value={valor}>
              {label}
            </option>
          ))}
        </select>
        <input
          placeholder="Nome"
          value={filtros.nome ?? ""}
          onChange={(e) => atualizarFiltro("nome", e.target.value)}
        />
        <input
          placeholder="Conselho"
          value={filtros.conselho ?? ""}
          onChange={(e) => atualizarFiltro("conselho", e.target.value)}
        />
        <input
          placeholder="Número do conselho"
          value={filtros.numero_conselho ?? ""}
          onChange={(e) => atualizarFiltro("numero_conselho", e.target.value)}
        />
        <input
          placeholder="Especialidade"
          value={filtros.especialidade ?? ""}
          onChange={(e) => atualizarFiltro("especialidade", e.target.value)}
        />
        <input
          type="date"
          value={filtros.data_inicial ?? ""}
          onChange={(e) => atualizarFiltro("data_inicial", e.target.value)}
        />
        <input
          type="date"
          value={filtros.data_final ?? ""}
          onChange={(e) => atualizarFiltro("data_final", e.target.value)}
        />
      </div>

      {erro && <p className="form-error">{erro}</p>}

      {dados && (
        <>
          <table>
            <thead>
              <tr>
                <th>Protocolo</th>
                <th>Nome</th>
                <th>Conselho</th>
                <th>Nº conselho</th>
                <th>Especialidade</th>
                <th>E-mail</th>
                <th>Telefone</th>
                <th>Data</th>
                <th>Status</th>
                <th>Responsável</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {dados.items.map((s) => (
                <tr key={s.id}>
                  <td>{s.protocolo}</td>
                  <td>{s.nome_completo}</td>
                  <td>{s.conselho}/{s.uf_conselho}</td>
                  <td>{s.numero_conselho}</td>
                  <td>{s.especialidade}</td>
                  <td>{s.email}</td>
                  <td>{s.telefone}</td>
                  <td>{new Date(s.created_at).toLocaleDateString("pt-BR")}</td>
                  <td>
                    <span className="badge">{STATUS_LABELS[s.status]}</span>
                  </td>
                  <td>{s.responsavel_nome ?? "-"}</td>
                  <td>
                    <Link to={`/admin/solicitacoes/${s.id}`}>Ver</Link>
                  </td>
                </tr>
              ))}
              {dados.items.length === 0 && (
                <tr>
                  <td colSpan={11}>Nenhuma solicitação encontrada.</td>
                </tr>
              )}
            </tbody>
          </table>

          <div className="paginacao">
            <button
              disabled={filtros.page <= 1}
              onClick={() => setFiltros((f) => ({ ...f, page: f.page - 1 }))}
            >
              Anterior
            </button>
            <span>
              Página {dados.page} de {totalPaginas} ({dados.total} solicitações)
            </span>
            <button
              disabled={filtros.page >= totalPaginas}
              onClick={() => setFiltros((f) => ({ ...f, page: f.page + 1 }))}
            >
              Próxima
            </button>
          </div>
        </>
      )}
    </div>
  );
}
