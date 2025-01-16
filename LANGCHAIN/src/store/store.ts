// store.ts
//@ts-ignore
import { createStore, Store } from 'vuex';

// store.ts

interface Message {
  text: string;
  isSender: boolean;
  timestamp: string;
}

interface Chat {
  id: string; // 每个聊天的唯一标识
  timestamp: string; // 创建聊天的时间
  messages: Message[]; // 当前聊天的消息
}

interface State {
  chats: Chat[];
}

const store = createStore<State>({
  state() {
    return {
      chats: [], // 初始化为空的聊天会话
      currentChatId: '' as string,
    };
  },
  mutations: {
    addChat(state: State) {
      const newChat: Chat = {
        id: new Date().toISOString(), // 使用时间戳作为聊天 ID
        timestamp: new Date().toISOString(),
        messages: [] // 每个聊天的消息列表初始化为空
      };
      state.chats.push(newChat);
    },
    addMessage(state: State, { chatId, message }: { chatId: string; message: Message }) {
      const chat = state.chats.find(c => c.id === chatId);
      if (chat) {
        chat.messages.push(message);
      }
    }
  },
  actions: {
    createNewChat({ commit }: { commit: Function }) {
      commit('addChat');
    },
    // 设置当前聊天 ID
    setCurrentChatId(state: any, chatId: string) {
      state.currentChatId = chatId;
    },
  }
});
  
export { store };
export type { Message, Chat, State}