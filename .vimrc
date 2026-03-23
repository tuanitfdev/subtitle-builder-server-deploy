set nocompatible
set noswapfile
set nu
set shiftwidth=2
set tabstop=2
set expandtab
set autoindent
set hlsearch
set incsearch
set smartcase
set ignorecase
set linebreak
set clipboard=unnamedplus
set pastetoggle=<F2>
set backspace=indent,eol,start
syntax on
colorscheme koehler
map <C-V> "+gP
imap <C-V> <Esc>"+gpa
cmap <C-V> <C-R>+

" Map phím \v để kích hoạt Visual Block Mode (Bôi đen theo cột)
" n: chế độ Normal, v: chế độ Visual
nnoremap <Leader>v <C-v>
vnoremap <Leader>v <C-v>

call plug#begin()

" List your plugins here
Plug 'ojroques/vim-oscyank', {'branch': 'main'}

call plug#end()

nmap <leader>c <Plug>OSCYankOperator
nmap <leader>cc <leader>c_
vmap <leader>c <Plug>OSCYankVisual