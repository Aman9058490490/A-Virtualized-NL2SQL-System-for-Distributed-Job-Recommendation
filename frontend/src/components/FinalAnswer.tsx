import React from 'react';
import { MessageSquare, Sparkles } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

interface FinalAnswerProps {
  answer: string;
}

// Simple function to convert markdown to formatted text
const formatMarkdownToText = (markdown: string): string => {
  let text = markdown;
  
  // Remove heading markers but keep the text
  text = text.replace(/^#{1,6}\s+/gm, '');
  
  // Convert bold **text** to plain text
  text = text.replace(/\*\*([^*]+)\*\*/g, '$1');
  
  // Convert italic *text* to plain text
  text = text.replace(/\*([^*]+)\*/g, '$1');
  
  // Convert bullet points to simple dashes
  text = text.replace(/^\*\s+/gm, '• ');
  
  // Remove extra blank lines
  text = text.replace(/\n{3,}/g, '\n\n');
  
  return text.trim();
};

export const FinalAnswer: React.FC<FinalAnswerProps> = ({ answer }) => {
  if (!answer) {
    return null;
  }

  const formattedAnswer = formatMarkdownToText(answer);

  return (
    <Card className="w-full border-primary/20 bg-gradient-to-br from-primary/5 to-primary/10">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-primary" />
          AI-Generated Answer
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex gap-3">
          <MessageSquare className="w-5 h-5 text-primary mt-1 flex-shrink-0" />
          <div className="text-base leading-relaxed whitespace-pre-wrap">
            {formattedAnswer}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
