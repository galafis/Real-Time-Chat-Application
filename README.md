# Real-Time Chat Application

[English](#english) | [Português](#português)

## English

### Overview
A modern real-time chat application built with Flask and Socket.IO, featuring user authentication, message history, typing indicators, and a responsive design. Perfect for team communication and real-time collaboration.

### Features
- **Real-time Messaging**: Instant message delivery using WebSocket technology
- **User Authentication**: Secure login and registration system
- **Message History**: Persistent message storage and retrieval
- **Typing Indicators**: See when other users are typing
- **Online Status**: Real-time user presence tracking
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **User Avatars**: Colorful avatar system for user identification
- **Room Support**: Multi-room chat functionality

### Technologies Used
- **Backend**: Python Flask, Flask-SocketIO
- **Frontend**: HTML5, CSS3, JavaScript, Socket.IO Client
- **Database**: SQLite for message and user storage
- **Real-time**: WebSocket communication
- **Security**: Password hashing, session management

### Architecture

#### Backend Components
1. **Flask Application**: Main web server and API endpoints
2. **Socket.IO Server**: Real-time WebSocket communication
3. **Database Layer**: SQLite with user and message management
4. **Authentication System**: Secure user registration and login

#### Frontend Components
1. **Chat Interface**: Modern, responsive chat UI
2. **Real-time Updates**: Live message updates and notifications
3. **User Management**: Online user tracking and display
4. **Responsive Design**: Mobile-friendly interface

### Installation

1. Clone the repository:
```bash
git clone https://github.com/galafis/Real-Time-Chat-Application.git
cd Real-Time-Chat-Application
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python chat_app.py
```

4. Open your browser to `http://localhost:5000`

### Usage

#### Getting Started
1. **Register**: Create a new account with username, email, and password
2. **Login**: Sign in with your credentials
3. **Join Chat**: Automatically join the General room
4. **Start Chatting**: Send messages and see real-time responses

#### Features Guide

##### Sending Messages
- Type your message in the input field
- Press Enter or click Send to deliver
- Messages appear instantly for all users

##### User Presence
- See who's online in the sidebar
- Online indicators show active users
- Join/leave notifications keep you informed

##### Typing Indicators
- See when others are typing
- Automatic timeout after 1 second of inactivity
- Non-intrusive display below chat area

### API Endpoints

#### Web Routes
- `GET /` - Main chat interface (requires authentication)
- `GET /login` - Login and registration page
- `POST /login` - Handle login/registration
- `GET /logout` - User logout
- `GET /api/messages/<room>` - Get message history

#### Socket.IO Events

##### Client to Server
- `join_room` - Join a chat room
- `send_message` - Send a message
- `typing` - Indicate typing status
- `stop_typing` - Stop typing indication

##### Server to Client
- `message` - New message received
- `user_joined` - User joined room
- `user_left` - User left room
- `typing` - User is typing
- `stop_typing` - User stopped typing
- `room_users` - Current room users

### Database Schema

#### Users Table
- `id` - Primary key
- `username` - Unique username
- `email` - User email address
- `password_hash` - Hashed password
- `avatar_color` - User avatar color
- `created_at` - Account creation timestamp
- `last_seen` - Last activity timestamp

#### Messages Table
- `id` - Primary key
- `room_name` - Chat room identifier
- `user_id` - Message sender ID
- `username` - Sender username
- `message` - Message content
- `message_type` - Message type (text, system)
- `timestamp` - Message timestamp

#### Chat Rooms Table
- `id` - Primary key
- `room_name` - Unique room identifier
- `room_description` - Room description
- `created_by` - Room creator ID
- `created_at` - Room creation timestamp
- `is_private` - Private room flag

### Security Features
- **Password Hashing**: SHA-256 password encryption
- **Session Management**: Secure user sessions
- **Input Validation**: Message length limits and sanitization
- **Authentication Required**: Protected routes and Socket.IO events

### Customization

#### Adding New Rooms
1. Insert room data into `chat_rooms` table
2. Update frontend room list
3. Implement room switching logic

#### Styling Customization
- Modify CSS variables for color schemes
- Update avatar color palette
- Customize message bubble styles

#### Feature Extensions
- File sharing capabilities
- Emoji support
- Message reactions
- Private messaging
- Voice/video calls

### Performance Optimization
- **Message Pagination**: Limit message history loading
- **Connection Management**: Efficient Socket.IO handling
- **Database Indexing**: Optimized queries
- **Caching**: Session and user data caching

### Deployment
- **Development**: Built-in Flask development server
- **Production**: Use Gunicorn with eventlet workers
- **Database**: Upgrade to PostgreSQL for production
- **Scaling**: Redis adapter for multi-server Socket.IO

### Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

### License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Português

### Visão Geral
Uma aplicação moderna de chat em tempo real construída com Flask e Socket.IO, apresentando autenticação de usuários, histórico de mensagens, indicadores de digitação e design responsivo. Perfeita para comunicação em equipe e colaboração em tempo real.

### Funcionalidades
- **Mensagens em Tempo Real**: Entrega instantânea de mensagens usando tecnologia WebSocket
- **Autenticação de Usuários**: Sistema seguro de login e registro
- **Histórico de Mensagens**: Armazenamento e recuperação persistente de mensagens
- **Indicadores de Digitação**: Veja quando outros usuários estão digitando
- **Status Online**: Rastreamento de presença de usuários em tempo real
- **Design Responsivo**: Funciona perfeitamente em dispositivos desktop e móveis
- **Avatares de Usuário**: Sistema de avatares coloridos para identificação de usuários
- **Suporte a Salas**: Funcionalidade de chat multi-salas

### Tecnologias Utilizadas
- **Backend**: Python Flask, Flask-SocketIO
- **Frontend**: HTML5, CSS3, JavaScript, Socket.IO Client
- **Banco de Dados**: SQLite para armazenamento de mensagens e usuários
- **Tempo Real**: Comunicação WebSocket
- **Segurança**: Hash de senhas, gerenciamento de sessões

### Arquitetura

#### Componentes Backend
1. **Aplicação Flask**: Servidor web principal e endpoints da API
2. **Servidor Socket.IO**: Comunicação WebSocket em tempo real
3. **Camada de Banco de Dados**: SQLite com gerenciamento de usuários e mensagens
4. **Sistema de Autenticação**: Registro e login seguros de usuários

#### Componentes Frontend
1. **Interface de Chat**: UI de chat moderna e responsiva
2. **Atualizações em Tempo Real**: Atualizações de mensagens ao vivo e notificações
3. **Gerenciamento de Usuários**: Rastreamento e exibição de usuários online
4. **Design Responsivo**: Interface amigável para dispositivos móveis

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/galafis/Real-Time-Chat-Application.git
cd Real-Time-Chat-Application
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute a aplicação:
```bash
python chat_app.py
```

4. Abra seu navegador em `http://localhost:5000`

### Uso

#### Começando
1. **Registrar**: Crie uma nova conta com nome de usuário, email e senha
2. **Login**: Entre com suas credenciais
3. **Entrar no Chat**: Entre automaticamente na sala Geral
4. **Começar a Conversar**: Envie mensagens e veja respostas em tempo real

#### Guia de Funcionalidades

##### Enviando Mensagens
- Digite sua mensagem no campo de entrada
- Pressione Enter ou clique em Enviar para entregar
- Mensagens aparecem instantaneamente para todos os usuários

##### Presença de Usuários
- Veja quem está online na barra lateral
- Indicadores online mostram usuários ativos
- Notificações de entrada/saída mantêm você informado

##### Indicadores de Digitação
- Veja quando outros estão digitando
- Timeout automático após 1 segundo de inatividade
- Exibição não intrusiva abaixo da área de chat

### Endpoints da API

#### Rotas Web
- `GET /` - Interface principal de chat (requer autenticação)
- `GET /login` - Página de login e registro
- `POST /login` - Lidar com login/registro
- `GET /logout` - Logout do usuário
- `GET /api/messages/<room>` - Obter histórico de mensagens

#### Eventos Socket.IO

##### Cliente para Servidor
- `join_room` - Entrar em uma sala de chat
- `send_message` - Enviar uma mensagem
- `typing` - Indicar status de digitação
- `stop_typing` - Parar indicação de digitação

##### Servidor para Cliente
- `message` - Nova mensagem recebida
- `user_joined` - Usuário entrou na sala
- `user_left` - Usuário saiu da sala
- `typing` - Usuário está digitando
- `stop_typing` - Usuário parou de digitar
- `room_users` - Usuários atuais da sala

### Esquema do Banco de Dados

#### Tabela Users
- `id` - Chave primária
- `username` - Nome de usuário único
- `email` - Endereço de email do usuário
- `password_hash` - Senha com hash
- `avatar_color` - Cor do avatar do usuário
- `created_at` - Timestamp de criação da conta
- `last_seen` - Timestamp da última atividade

#### Tabela Messages
- `id` - Chave primária
- `room_name` - Identificador da sala de chat
- `user_id` - ID do remetente da mensagem
- `username` - Nome de usuário do remetente
- `message` - Conteúdo da mensagem
- `message_type` - Tipo de mensagem (texto, sistema)
- `timestamp` - Timestamp da mensagem

#### Tabela Chat Rooms
- `id` - Chave primária
- `room_name` - Identificador único da sala
- `room_description` - Descrição da sala
- `created_by` - ID do criador da sala
- `created_at` - Timestamp de criação da sala
- `is_private` - Flag de sala privada

### Funcionalidades de Segurança
- **Hash de Senhas**: Criptografia de senhas SHA-256
- **Gerenciamento de Sessões**: Sessões de usuário seguras
- **Validação de Entrada**: Limites de comprimento de mensagem e sanitização
- **Autenticação Obrigatória**: Rotas protegidas e eventos Socket.IO

### Personalização

#### Adicionando Novas Salas
1. Inserir dados da sala na tabela `chat_rooms`
2. Atualizar lista de salas do frontend
3. Implementar lógica de troca de salas

#### Personalização de Estilo
- Modificar variáveis CSS para esquemas de cores
- Atualizar paleta de cores de avatar
- Personalizar estilos de bolhas de mensagem

#### Extensões de Funcionalidades
- Capacidades de compartilhamento de arquivos
- Suporte a emojis
- Reações a mensagens
- Mensagens privadas
- Chamadas de voz/vídeo

### Otimização de Performance
- **Paginação de Mensagens**: Limitar carregamento de histórico de mensagens
- **Gerenciamento de Conexões**: Manuseio eficiente do Socket.IO
- **Indexação de Banco de Dados**: Consultas otimizadas
- **Cache**: Cache de dados de sessão e usuário

### Deploy
- **Desenvolvimento**: Servidor de desenvolvimento Flask integrado
- **Produção**: Use Gunicorn com workers eventlet
- **Banco de Dados**: Upgrade para PostgreSQL para produção
- **Escalabilidade**: Adaptador Redis para Socket.IO multi-servidor

### Contribuindo
1. Faça um fork do repositório
2. Crie uma branch de feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adicionar nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

### Licença
Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

