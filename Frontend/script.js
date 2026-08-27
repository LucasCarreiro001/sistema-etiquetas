/* ==========================================================
   CONFIGURAÇÃO
   ========================================================== */
const API_BASE = "http://127.0.0.1:8000"; // ajuste para o IP do servidor quando for para produção

/* Estado da sessão (em memória — perdido ao recarregar a página,
   igual a como o token expira sozinho depois de 36h de qualquer forma) */
let token = null;
let usuarioNome = null;
let categoriaAtual = null;
let produtoSelecionado = null;
let quantidadeAtual = 1;

/* ==========================================================
   HELPERS DE NAVEGAÇÃO ENTRE TELAS
   ========================================================== */
function mostrarView(id) {
  document.querySelectorAll(".view").forEach(v => v.classList.remove("ativa"));
  document.getElementById(id).classList.add("ativa");
}

function mostrarHeader(mostrar) {
  document.getElementById("app-header").style.display = mostrar ? "flex" : "none";
}

function mostrarErro(elId, mensagem) {
  const el = document.getElementById(elId);
  el.textContent = mensagem;
  el.classList.add("mostrar");
}

function limparErro(elId) {
  const el = document.getElementById(elId);
  el.classList.remove("mostrar");
  el.textContent = "";
}

/* ==========================================================
   CHAMADAS À API
   ========================================================== */
async function apiFetch(caminho, opcoes = {}) {
  const headers = opcoes.headers || {};
  if (token) headers["Authorization"] = "Bearer " + token;
  if (opcoes.body) headers["Content-Type"] = "application/json";

  const resposta = await fetch(API_BASE + caminho, { ...opcoes, headers });

  if (resposta.status === 401) {
    // token expirado ou inválido — volta pro login
    token = null;
    mostrarHeader(false);
    mostrarView("login-view");
    mostrarErro("login-erro", "Sua sessão expirou. Faça login novamente.");
    throw new Error("Não autenticado");
  }

  if (!resposta.ok) {
    const dado = await resposta.json().catch(() => ({}));
    throw new Error(dado.detail || "Erro ao comunicar com o servidor");
  }

  return resposta.json();
}

/* ==========================================================
   LOGIN
   ========================================================== */
document.getElementById("btn-login").addEventListener("click", fazerLogin);
document.getElementById("login-senha").addEventListener("keydown", e => {
  if (e.key === "Enter") fazerLogin();
});

async function fazerLogin() {
  limparErro("login-erro");
  const email = document.getElementById("login-email").value.trim();
  const senha = document.getElementById("login-senha").value;

  if (!email || !senha) {
    mostrarErro("login-erro", "Preencha e-mail e senha.");
    return;
  }

  const btn = document.getElementById("btn-login");
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Entrando...';

  try {
    const dado = await apiFetch("/login", {
      method: "POST",
      body: JSON.stringify({ email, senha })
    });
    token = dado.access_token;

    // busca o nome de quem logou a partir do token decodificado no payload
    const payload = JSON.parse(atob(token.split(".")[1]));
    usuarioNome = payload.nome || email.split("@")[0];

    document.getElementById("saudacao-nome").textContent = "Olá, " + usuarioNome;
    document.getElementById("login-email").value = "";
    document.getElementById("login-senha").value = "";

    mostrarHeader(true);
    mostrarView("categorias-view");
  } catch (err) {
    mostrarErro("login-erro", "E-mail ou senha incorretos.");
  } finally {
    btn.disabled = false;
    btn.textContent = "Entrar";
  }
}

document.getElementById("btn-sair").addEventListener("click", () => {
  token = null;
  usuarioNome = null;
  mostrarHeader(false);
  mostrarView("login-view");
});

/* ==========================================================
   CATEGORIAS
   ========================================================== */
document.querySelectorAll(".tile-categoria").forEach(tile => {
  tile.addEventListener("click", () => {
    categoriaAtual = tile.dataset.categoria;
    const nomesLegiveis = { padaria: "Padaria", confeitaria: "Confeitaria", bebidas: "Bebidas", comidas: "Comidas" };
    document.getElementById("titulo-categoria").textContent = nomesLegiveis[categoriaAtual];
    document.getElementById("input-busca").value = "";
    carregarProdutosPorCategoria(categoriaAtual);
    mostrarView("produtos-view");
  });
});

document.getElementById("btn-voltar-categorias").addEventListener("click", () => mostrarView("categorias-view"));
document.getElementById("btn-voltar-categorias-sucesso").addEventListener("click", () => mostrarView("categorias-view"));

/* ==========================================================
   LISTA / BUSCA DE PRODUTOS
   ========================================================== */
async function carregarProdutosPorCategoria(categoria) {
  const lista = document.getElementById("lista-produtos");
  lista.innerHTML = '<p style="text-align:center; color:var(--texto-suave); padding:30px 0;">Carregando...</p>';
  try {
    const produtos = await apiFetch(`/produtos/categoria/${categoria}`);
    renderizarProdutos(produtos);
  } catch (err) {
    lista.innerHTML = '<p style="text-align:center; color:var(--erro); padding:30px 0;">Não foi possível carregar os produtos.</p>';
  }
}

let debounceBusca = null;
document.getElementById("input-busca").addEventListener("input", (e) => {
  clearTimeout(debounceBusca);
  const termo = e.target.value.trim();
  debounceBusca = setTimeout(() => {
    if (termo.length === 0) {
      carregarProdutosPorCategoria(categoriaAtual);
    } else {
      buscarProdutos(termo);
    }
  }, 300);
});

async function buscarProdutos(termo) {
  try {
    const produtos = await apiFetch(`/produtos/buscar?nome=${encodeURIComponent(termo)}`);
    // filtra pela categoria atual no cliente, já que a busca da API pesquisa em todas
    renderizarProdutos(produtos.filter(p => p.categoria === categoriaAtual));
  } catch (err) {
    document.getElementById("lista-produtos").innerHTML =
      '<p style="text-align:center; color:var(--erro); padding:30px 0;">Erro na busca.</p>';
  }
}

function renderizarProdutos(produtos) {
  const lista = document.getElementById("lista-produtos");

  if (produtos.length === 0) {
    lista.innerHTML = `
      <div class="estado-vazio">
        <span class="emoji">🔍</span>
        <p>Nenhum produto encontrado nesta categoria.</p>
      </div>`;
    return;
  }

  lista.innerHTML = "";
  produtos.forEach(produto => {
    const card = document.createElement("div");
    card.className = "card-produto";
    card.innerHTML = `
      <div>
        <div class="nome">${produto.nome}</div>
        <div class="meta">${produto.validade_valor} ${produto.validade_unidade} · ${rotuloArmazenamento(produto.armazenamento)}</div>
      </div>
      <span class="seta">→</span>
    `;
    card.addEventListener("click", () => abrirDetalheProduto(produto));
    lista.appendChild(card);
  });
}

function rotuloArmazenamento(valor) {
  const mapa = { refrigerado: "Refrigerado", congelado: "Congelado", "temperatura ambiente": "Ambiente" };
  return mapa[valor] || valor;
}

function classeArmazenamento(valor) {
  const mapa = { refrigerado: "tag-refrigerado", congelado: "tag-congelado", "temperatura ambiente": "tag-ambiente" };
  return mapa[valor] || "tag-ambiente";
}

/* ==========================================================
   DETALHE DO PRODUTO
   ========================================================== */
document.getElementById("btn-voltar-produtos").addEventListener("click", () => mostrarView("produtos-view"));

function abrirDetalheProduto(produto) {
  produtoSelecionado = produto;
  quantidadeAtual = 1;
  document.getElementById("qtd-etiquetas").textContent = quantidadeAtual;
  limparErro("gerar-erro");

  document.getElementById("detalhe-nome").textContent = produto.nome;
  document.getElementById("detalhe-validade").textContent =
    `${produto.validade_valor} ${produto.validade_unidade}` +
    (produto.validade_referencia === "fim_do_dia" ? " (até o fim do dia)" : "");

  const elArm = document.getElementById("detalhe-armazenamento");
  elArm.innerHTML = `<span class="tag-armazenamento ${classeArmazenamento(produto.armazenamento)}">${rotuloArmazenamento(produto.armazenamento)}</span>`;

  const linhaPorcao = document.getElementById("linha-porcao");
  if (produto.quantidade_padrao && produto.quantidade_unidade) {
    let valor = produto.quantidade_padrao;
    if (valor === Math.floor(valor)) valor = Math.floor(valor);
    document.getElementById("detalhe-porcao").textContent = `${valor}${produto.quantidade_unidade}`;
    linhaPorcao.style.display = "flex";
  } else {
    linhaPorcao.style.display = "none";
  }

  mostrarView("detalhe-view");
}

document.getElementById("btn-menos").addEventListener("click", () => {
  if (quantidadeAtual > 1) {
    quantidadeAtual--;
    document.getElementById("qtd-etiquetas").textContent = quantidadeAtual;
  }
});
document.getElementById("btn-mais").addEventListener("click", () => {
  quantidadeAtual++;
  document.getElementById("qtd-etiquetas").textContent = quantidadeAtual;
});

/* ==========================================================
   GERAR ETIQUETA
   ========================================================== */
document.getElementById("btn-gerar").addEventListener("click", gerarEtiqueta);

async function gerarEtiqueta() {
  limparErro("gerar-erro");
  const btn = document.getElementById("btn-gerar");
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Gerando...';

  try {
    const etiqueta = await apiFetch("/etiquetas/gerar", {
      method: "POST",
      body: JSON.stringify({ produto_id: produtoSelecionado.id, quantidade: quantidadeAtual })
    });

    // TODO: quando a impressora estiver conectada, o backend passa a enviar
    // o comando ZPL automaticamente dentro dessa mesma rota — nada muda aqui no front.
    montarMiniEtiqueta(etiqueta);
    mostrarView("sucesso-view");

    // reinicia a animação do selo toda vez que essa tela é exibida de novo
    const selo = document.querySelector(".selo-cera");
    selo.style.animation = "none";
    void selo.offsetWidth;
    selo.style.animation = null;

  } catch (err) {
    mostrarErro("gerar-erro", err.message || "Não foi possível gerar a etiqueta.");
  } finally {
    btn.disabled = false;
    btn.textContent = "Gerar etiqueta";
  }
}

function formatarDataHora(iso) {
  const d = new Date(iso);
  return d.toLocaleString("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" });
}

function montarMiniEtiqueta(etiqueta) {
  const el = document.getElementById("mini-etiqueta");
  el.innerHTML = `
    <div class="prod">${etiqueta.produto_nome}</div>
    <div class="linha"><span>Manipulado por</span><span>${etiqueta.manipulado_por}</span></div>
    <div class="linha"><span>Manipulação</span><span>${formatarDataHora(etiqueta.manipulado_em)}</span></div>
    <div class="linha"><span>Validade</span><span>${formatarDataHora(etiqueta.validade)}</span></div>
    <div class="linha"><span>Armazenamento</span><span>${rotuloArmazenamento(etiqueta.armazenamento)}</span></div>
    ${etiqueta.porcao_padrao ? `<div class="linha"><span>Porção</span><span>${etiqueta.porcao_padrao}</span></div>` : ""}
    <div class="linha"><span>Quantidade</span><span>${etiqueta.quantidade} etiqueta(s)</span></div>
  `;
}

document.getElementById("btn-nova-etiqueta").addEventListener("click", () => {
  mostrarView("produtos-view");
});

/* ==========================================================
   HISTÓRICO
   ========================================================== */
document.getElementById("btn-ver-historico").addEventListener("click", abrirHistorico);
document.getElementById("btn-historico-header").addEventListener("click", abrirHistorico);
document.getElementById("btn-voltar-de-historico").addEventListener("click", () => mostrarView("categorias-view"));

async function abrirHistorico() {
  mostrarView("historico-view");
  const lista = document.getElementById("lista-historico");
  lista.innerHTML = '<p style="text-align:center; color:var(--texto-suave); padding:30px 0;">Carregando...</p>';

  try {
    const etiquetas = await apiFetch("/etiquetas");
    if (etiquetas.length === 0) {
      lista.innerHTML = `
        <div class="estado-vazio">
          <span class="emoji">📋</span>
          <p>Nenhuma etiqueta gerada ainda.</p>
        </div>`;
      return;
    }
    lista.innerHTML = "";
    etiquetas.forEach(item => {
      const div = document.createElement("div");
      div.className = "item-historico";
      div.innerHTML = `
        <div class="topo">
          <span class="nome-produto">${item.produto_nome}</span>
          <span class="qtd-badge">${item.quantidade}x</span>
        </div>
        <div class="detalhes">
          ${item.manipulado_por} · ${formatarDataHora(item.manipulado_em)} · vence ${formatarDataHora(item.validade)}
        </div>
      `;
      lista.appendChild(div);
    });
  } catch (err) {
    lista.innerHTML = '<p style="text-align:center; color:var(--erro); padding:30px 0;">Não foi possível carregar o histórico.</p>';
  }
}